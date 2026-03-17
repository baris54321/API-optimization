import asyncio
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse, Response
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db, AsyncSessionLocal
from models import AppUser, AppPost, AppComment
from schemas import UserOut, PostOut, UserDetailOut

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppUser))
    users = result.scalars().all()
    return users

@router.get("/v1/{user_id}", response_model=UserDetailOut)
async def get_user_detail_v2(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AppUser).where(AppUser.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts_result = await db.execute(
        select(AppPost)
        .where(AppPost.author_id == user_id)
        .options(selectinload(AppPost.comments))
        .order_by(AppPost.id)
    )
    posts = posts_result.scalars().all()

    return UserDetailOut(
        user=UserOut.model_validate(user),
        posts=[PostOut.model_validate(p) for p in posts],
    )

@router.get("/v2/{user_id}")
async def get_user_detail_v1(user_id: int, db: AsyncSession = Depends(get_db)):
    user_row = (await db.execute(
        select(AppUser.id, AppUser.username, AppUser.email)
        .where(AppUser.id == user_id)
    )).one_or_none()

    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")

    author_posts_subq = select(AppPost.id).where(AppPost.author_id == user_id)

    async def fetch_posts():
        async with AsyncSessionLocal() as s:
            return (await s.execute(
                select(AppPost.id, AppPost.title, AppPost.body, AppPost.created_at, AppPost.updated_at)
                .where(AppPost.author_id == user_id)
                .order_by(AppPost.id)
            )).all()

    async def fetch_comments():
        async with AsyncSessionLocal() as s:
            return (await s.execute(
                select(AppComment.id, AppComment.text, AppComment.created_at, AppComment.post_id)
                .where(AppComment.post_id.in_(author_posts_subq))
                .order_by(AppComment.post_id, AppComment.id)
            )).all()

    posts_rows, comments_rows = await asyncio.gather(fetch_posts(), fetch_comments())

    comments_by_post = defaultdict(list)
    for c in comments_rows:
        comments_by_post[c.post_id].append({
            "id": c.id, "text": c.text, "created_at": c.created_at,
        })

    return ORJSONResponse({
        "user": {"id": user_row.id, "username": user_row.username, "email": user_row.email},
        "posts": [
            {
                "id": p.id, "title": p.title, "body": p.body,
                "created_at": p.created_at, "updated_at": p.updated_at,
                "comments": comments_by_post.get(p.id, []),
            }
            for p in posts_rows
        ],
    })


USER_DETAIL_SQL = text("""
    WITH post_comments AS (
        SELECT
            p.id, p.title, p.body, p.created_at,
            COALESCE(
                json_agg(
                    json_build_object(
                        'id',         c.id,
                        'text',       c.text,
                        'created_at', c.created_at
                    ) ORDER BY c.id
                ) FILTER (WHERE c.id IS NOT NULL),
                '[]'::json
            ) AS comments
        FROM app_post p
        LEFT JOIN app_comment c ON c.post_id = p.id
        WHERE p.author_id = :user_id
        GROUP BY p.id
    )
    SELECT json_build_object(
        'user', json_build_object(
            'id',       u.id,
            'username', u.username,
            'email',    u.email
        ),
        'posts', COALESCE(
            (SELECT json_agg(
                json_build_object(
                    'id',         pc.id,
                    'title',      pc.title,
                    'body',       pc.body,
                    'created_at', pc.created_at,
                    'comments',   pc.comments
                ) ORDER BY pc.id
            ) FROM post_comments pc),
            '[]'::json
        )
    )::text
    FROM app_user u
    WHERE u.id = :user_id
""")


@router.get("/v3/{user_id}")
async def get_user_detail_v3(user_id: int, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(USER_DETAIL_SQL, {"user_id": user_id})).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(content=row, media_type="application/json")