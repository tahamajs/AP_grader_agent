# This is a help file for SSH for AP-F03

add key in `ssh.txt` like this:

```shell
touch ~/.ssh/id_rsa_ap_f03
nano ~/.ssh/id_rsa_ap_f03
```

paste it there, then

```shell
chmod 600 ~/.ssh/id_rsa_ap_f03
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa_ap_f03
nano ~/.ssh/config
```

and then

```shell
# Default GitHub account (first account)
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa

# Temp AP account
Host AP-F03
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa_ap_f03
```

then test it like this

```shell
ssh -T git@AP-F03
```
