from _cffi_backend import _CDataBase

class CData(_CDataBase): ... # type: ignore

class _CSignatureTime(CData):
    time: int
    offset: int

class _CSignature(CData):
    name: _CDataBase
    email: _CDataBase
    when: _CSignatureTime

class _COid(CData):
    id: _CDataBase

class _CHunk(CData):
    boundary: CData
    final_commit_id: _COid
    final_signature: _CSignature
    final_start_line_number: int
    lines_in_hunk: int
    orig_commit_id: _COid
    orig_path: _CDataBase
    orig_signature: _CSignature
    orig_start_line_number: int

class _CConfigEntry(CData):
    backend_type: _CDataBase
    free: _CDataBase
    include_depth: int
    level: int
    name: _CDataBase
    origin_path: _CDataBase
    value: _CDataBase
