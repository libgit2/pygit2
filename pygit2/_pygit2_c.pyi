from typing import NewType, Generic, Literal, TypeVar, overload

T = TypeVar('T')

char = NewType('char', object)
char_pointer = NewType('char_pointer', object)

class _Pointer(Generic[T]):
    @overload
    def __getitem__(self, item: Literal[0]) -> T: ...
    @overload
    def __getitem__(self, item: slice[None, None, None]) -> bytes: ...

class GitTimeC:
    # incomplete
    time: int
    offset: int

class GitSignatureC:
    name: char_pointer
    email: char_pointer
    when: GitTimeC

class GitHunkC:
    # incomplete
    boundary: char
    final_start_line_number: int
    final_signature: GitSignatureC
    orig_signature: GitSignatureC
    orig_start_line_number: int
    orig_path: str
    lines_in_hunk: int

class GitBlameC:
    # incomplete
    pass
