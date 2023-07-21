from typing import Optional, Union


class JsonApiError(RuntimeError):
    def __init__(
        self,
        id_: Optional[Union[str, int]] = None,
        http_status: Optional[Union[str, int]] = None,
        code: Optional[Union[str, int]] = None,
        title: Optional[str] = None,
        detail: Optional[str] = None,
        source: Optional[dict] = None,
    ):
        self.id = id_
        self.http_status = http_status
        self.code = code
        self.title = title
        self.detail = detail
        self.source = source
        super().__init__(id_, http_status, code, title, detail, source)
