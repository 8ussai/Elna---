from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from backend.schemas.post import PostCreate, PostOut, PostVoteAction
from backend.database import get_db
from backend.models.user import User
from backend.models.post import Post, PostVote
from backend.core.apiDependencies import get_current_user


router = APIRouter()


class PostFilter(str, Enum):
    university = "university"
    college = "college"
    major = "major"


def _map_to_post_out(post: Post, votes_count: int) -> PostOut:
    return PostOut(
        id=post.id,
        user_id=post.user_id,
        content=post.content,
        university=post.university,
        college=post.college,
        major=post.major,
        created_at=post.created_at,
        votes_count=votes_count,
    )


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_post = Post(
        user_id=current_user.id,
        content=post_data.content,
        university=current_user.university,
        college=current_user.college,
        major=current_user.major,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return _map_to_post_out(new_post, 0)


@router.get("/", response_model=list[PostOut])
def get_posts(
    filter_by: Optional[PostFilter] = Query(
        default=None,
        description="Filter posts by 'university', 'college', or 'major'."
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(
        Post,
        func.coalesce(func.sum(PostVote.vote_dir), 0).label('votes_count')
    ).outerjoin(PostVote, Post.id == PostVote.post_id)

    if filter_by == PostFilter.university:
        query = query.filter(Post.university == current_user.university)
    elif filter_by == PostFilter.college:
        query = query.filter(Post.college == current_user.college)
    elif filter_by == PostFilter.major:
        query = query.filter(Post.major == current_user.major)

    results = query.group_by(Post.id).order_by(Post.created_at.desc()).all()

    return [_map_to_post_out(post, votes) for post, votes in results]


@router.post("/{post_id}/vote", status_code=status.HTTP_200_OK)
def vote_post(
    post_id: int,
    vote_action: PostVoteAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vote_dir = vote_action.vote_dir

    if vote_dir not in (1, -1):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="vote_dir must be 1 (upvote) or -1 (downvote).",
        )

    # make sure the post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found.",
        )

    existing_vote = (
        db.query(PostVote)
        .filter(PostVote.post_id == post_id, PostVote.user_id == current_user.id)
        .first()
    )

    if existing_vote is None:
        new_vote = PostVote(
            post_id=post_id,
            user_id=current_user.id,
            vote_dir=vote_dir,
        )
        db.add(new_vote)
        db.commit()
        return {"message": "Vote added.", "vote_dir": vote_dir}

    if existing_vote.vote_dir == vote_dir:
        db.delete(existing_vote)
        db.commit()
        return {"message": "Vote removed.", "vote_dir": 0}

    existing_vote.vote_dir = vote_dir
    db.commit()
    return {"message": "Vote updated.", "vote_dir": vote_dir}