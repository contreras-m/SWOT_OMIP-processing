from ftplib import FTP
import os


host = "ftp-access.aviso.altimetry.fr"
user = "XXX"
password = "XXX"
cycle="010"

os.makedirs((f"cycle_{cycle}"), exist_ok=True)
os.chdir((f"cycle_{cycle}"))
remote_dir = (f"/swot_products/l3_karin_nadir/l3_lr_ssh/v3_0/Expert/reproc/cycle_{cycle}")


def run_download(host,user,password ,remote_dir):
    ftp = FTP()
    ftp.connect(host, 21)
    ftp.login(user, password)

    ftp.cwd(remote_dir)

    files = ftp.nlst()
    print("Files:", files)

    for f in files:
        if f.endswith(".nc"):

            if os.path.exists(f):
                print(f"Skipping {f} (already exists)")
                continue

            print("Downloading", f)
            with open(f, "wb") as local_file:
                ftp.retrbinary(f"RETR " + f, local_file.write)

    ftp.quit()
    return


run_download(host,user,password,remote_dir)
os.chdir("..")
