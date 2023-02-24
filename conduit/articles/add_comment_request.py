from dataclasses import dataclass


@dataclass
class AddCommentRequestComment:
    body: str


@dataclass
class AddCommentRequest:
    comment: AddCommentRequestComment
