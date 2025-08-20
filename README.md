# Setup

```bash
git clone git@github.com:allllpina/lirili-larila.git
cd lirili-larila
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

You'll also need to copy a pair of public/private SSH RSA keys into the `.ssh` folder. Currently there is a public example key in there used in the `examples/verify_jwt_rsa256_ssh.py` file but to use the `examples/create_jwt_rsa256_ssh.py` you'll need either a private key under the `.ssh` folder or to adjust the path to a preexisting folder.

```console
ssh-keygen -t rsa -f ~/lirili-larila/.ssh/id_rsa
```

## Running scripts

```console
python examples/verify_jwt_rsa256_ssh.py
```

## Scripts Description

| Script                                 | Description                                                                       |
| -------------------------------------- | --------------------------------------------------------------------------------- |
| `examples/create_jwt_hs256.py`         | Creates and prints out a JWT using the **HS256** algorithm                        |
| `examples/create_jwt_rs256_ssh.py`     | Creates and prints out a JWT using the **RS256** algorithm                        |
| `examples/handle_expired_error_jwt.py` | Tries to decode an expired token and prints out the error elegantly when it fails |
| `examples/verify_jwt_hs256.py`         | Verifies and prints out the payload of a JWT signed with the **HS256** algorithm  |
| `examples/verify_jwt_rs256_ssh.py`     | Verifies and prints out the payload of a JWT signed with the **RS256** algorithm  |

## Wrapping up

If you ran into any issues, reach out in the [comments of the blog post](https://auth0.com/blog/how-to-handle-jwt-in-python) or [feel free to tweet me](https://twitter.com/jesstemporal). Thanks!
