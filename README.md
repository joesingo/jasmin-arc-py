# jasmin-arc-py
Python library for connecting to ARC CE services on JASMIN

## Usage

### Config

`jasmin_arc` uses a JSON config file to configure the connection to the ARC CE server.
The required options are:
* `pem_file`: **Description here** (default: `~/.arc/userkey-nopass.pem`)

* `client_cert_file`: **Description here** (default: `~/.arc/usercert.pem`)

* `browser_cert_file`: **Description here** (default: `~/certBundle.p12`)

* `certs_dir`: **Description here** (default: `/etc/grid-security/certificates`)

* `arc_proxy_cmd`: **Description here** (default: `/usr/bin/arcproxy`)

* `myproxy_file`: **Description here** (default: `/tmp/x509up_u502`)

* `arc_server`: URL to the ARC server (default: `jasmin-ce.ceda.ac.uk:60000/arex`)

* `outputs_filename`: The name of the file that will be retrieved when saving job outputs. This
  should match the location output is written to in your job scripts. (default: `outputs.zip`)

* `errors_filename`: Similar to `outputs_filename` but for error output. (default: `errors_file.txt`)


## Tests

To run the tests, use:
```bash
python tests/tests.py
```

