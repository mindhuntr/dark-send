## Obtained from https://gist.github.com/xrayw/4d537d0f2b94c7e37f106d4e51210495 
## Modified to display cumulative progress callback 

import asyncio
import hashlib
import os
from typing import Optional

from telethon import TelegramClient, custom, helpers, hints, utils
from telethon.crypto import AES
from telethon.tl import functions, types, TLRequest


class TelegramUploadClient(TelegramClient):

    def __init__(self, *args, concurrent: int = 10, **kwargs):
        self.concurrent = concurrent
        self.upload_semaphore = asyncio.Semaphore(concurrent)
        super().__init__(*args, **kwargs)

    async def upload_file(
        self: 'TelegramUploadClient',
        file: 'hints.FileLike',
        *,
        part_size_kb: float | None = None,
        file_size: int | None = None,
        file_name: str | None = None,
        use_cache: type | None = None,
        key: bytes | None = None,
        iv: bytes | None = None,
        progress_callback: 'hints.ProgressCallback | None' = None
    ) -> 'types.TypeInputFile':

        if isinstance(file, (types.InputFile, types.InputFileBig)):
            return file  # Already uploaded

        async with helpers._FileStream(file) as stream:
            file_size = stream.file_size
            assert file_size is not None

            # Determine optimal chunk size
            if not part_size_kb:
                part_size_kb = utils.get_appropriated_part_size(file_size)

            if part_size_kb > 512:
                raise ValueError('The part size must be <= 512KB')

            part_size = int(part_size_kb * 1024)
            if part_size % 1024 != 0:
                raise ValueError('The part size must be evenly divisible by 1024')

            file_id = helpers.generate_random_long()
            if not file_name:
                file_name = stream.name or str(file_id)

            if file_name and not os.path.splitext(file_name)[-1]:
                file_name += utils._get_extension(stream)

            is_big = file_size > 10 * 1024 * 1024
            hash_md5 = hashlib.md5()
            part_count = (file_size + part_size - 1) // part_size

            # Shared progress tracking
            uploaded_bytes = 0
            progress_lock = asyncio.Lock()

            async def _update_progress(increment: int):
                nonlocal uploaded_bytes
                async with progress_lock:
                    uploaded_bytes += increment
                    if progress_callback:
                        await helpers._maybe_await(progress_callback(uploaded_bytes, file_size))

            tasks = []
            for part_index in range(part_count):
                # Read the file chunk
                part = await helpers._maybe_await(stream.read(part_size))
                if not isinstance(part, bytes):
                    raise TypeError(
                        f'file descriptor returned {type(part)}, not bytes (must be opened in bytes mode)'
                    )

                # Validate chunk length
                if len(part) != part_size and part_index < part_count - 1:
                    raise ValueError(
                        f'read less than {part_size} before reaching the end; either file_size or read() are wrong'
                    )

                # Optional encryption
                if key and iv:
                    part = AES.encrypt_ige(part, key, iv)

                # Hashing for small files
                if not is_big:
                    hash_md5.update(part)

                # Choose request type
                if is_big:
                    request = functions.upload.SaveBigFilePartRequest(file_id, part_index, part_count, part)
                else:
                    request = functions.upload.SaveFilePartRequest(file_id, part_index, part)

                await self.upload_semaphore.acquire()
                task = self.loop.create_task(
                    self._send_file_part(
                        request=request,
                        part_index=part_index,
                        part_count=part_count,
                        part_size=len(part),
                        update_progress=_update_progress,
                    ),
                    name=f"telegram-upload-file-{part_index}"
                )
                tasks.append(task)

            await asyncio.wait(tasks)

        if is_big:
            return types.InputFileBig(file_id, part_count, file_name)
        else:
            return custom.InputSizedFile(file_id, part_count, file_name, md5=hash_md5, size=file_size)

    async def _send_file_part(
        self,
        request: TLRequest,
        part_index: int,
        part_count: int,
        part_size: int,
        update_progress,
    ) -> None:

        try:
            result = await self(request)
            await update_progress(part_size)
        finally:
            self.upload_semaphore.release()
