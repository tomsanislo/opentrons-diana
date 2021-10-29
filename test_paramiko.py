import paramiko, os
from scp import SCPClient


k = paramiko.RSAKey.from_private_key_file(os.path.join(os.path.expanduser("~"), "dl_ot2_ssh_key"))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect("192.168.10.194", username="root", pkey=k)
scp = SCPClient(ssh.get_transport())

# scp = paramiko.
# ssh.exec_command("cd /data/user_storage/")
cmd = "cd /data/user_storage/ && opentrons_execute /data/user_storage/opentrons2.py"
# ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
scp.put(os.path.join(os.path.expanduser("~"), "OneDrive - Diana Biotechnologies, s.r.o", "Desktop", "opentrons_testing", "opentrons2.py"),
                recursive=True,
                remote_path="/data/user_storage"
            )
# print(str(ssh_stderr))
ssh.exec_command(cmd)
ssh.close()
