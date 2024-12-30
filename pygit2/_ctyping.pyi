from _cffi_backend import _CDataBase

class CData(_CDataBase): ... # type: ignore

class _CSignatureTime(CData):
    time: int
    offset: int

class _CSignature(CData):
    name: CData
    email: CData
    when: _CSignatureTime

class _COid(CData):
    id: CData

class _CHunk(CData):
    boundary: CData
    final_commit_id: _COid
    final_signature: _CSignature
    final_start_line_number: int
    lines_in_hunk: int
    orig_commit_id: _COid
    orig_path: str
    orig_signature: _CSignature
    orig_start_line_number: int

