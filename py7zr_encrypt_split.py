from pathlib import Path
from multivolumefile import MultiVolume
from py7zr import SevenZipFile, FILTER_COPY

# Encrypt and split a single file with 7z
def sevenzip(fpath: Path | str, password: str | None = None, volume_size: int | None = None):
    filters = [{"id": FILTER_COPY}]
    fpath = Path(fpath)
    fsize = fpath.stat().st_size

    # Set split size above the sise of the file if not volume size especified
    if not volume_size:
        volume_size = fsize + 1024

    # Determine the amount of extension digits are necessary, with a minimum of 3
    ext_digits = len(str(fsize // volume_size + 1))
    if ext_digits < 3:
        ext_digits = 3

    with MultiVolume(
        fpath.with_name(fpath.name + ".7z"), mode="wb", volume=volume_size, ext_digits=ext_digits
    ) as archive:
        with SevenZipFile(archive, "w", filters=filters, password=password) as archive_writer:
            if password:
                archive_writer.set_encoded_header_mode(True)
                archive_writer.set_encrypted_header(True)

            archive_writer.write(fpath, fpath.name)

    files = []
    for file in archive._files:
        files.append(file.name)

    return files
