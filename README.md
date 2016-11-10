[![Latest Version](http://img.shields.io/badge/latest-0.2.0-brightgreen.svg)](https://github.com/rholder/dynq/releases/tag/v0.2.0) [![License](http://img.shields.io/badge/license-apache%202-brightgreen.svg)](https://github.com/rholder/dynq/blob/master/LICENSE)

##What is this?
`dynq`, short for DynamoDB Query, is a commandline client for pulling data out of DynamoDB. Its primary function is to
expose a minimal API for querying DynamoDB in a `key=value` format and then return data that can be directly piped or
sourced into a shell script's environment. For example:

```bash
dynq --table-name deployment --key-value environment=gozer-dev
```
might return the following:

```bash
environment=gozer-dev
db_host="temple.of.gozer"
run_script="zuul --find-keymaster vinz"
```

If `dynq` fails in any way, it should raise a non-zero exit code on termination.

##Features
* Single minified binary install, all you need is Python on your path for OSX or Linux
* Query DynamoDB in a simple `key=value` format
* Return content in a directly shell sourceable format
* Uses boto under the hood so all boto configuration options are picked up and available

##Installation
`dynq` is just a single binary that you can drop anywhere you feel like on a *nix based system (sorry Windows, maybe
it works with Cygwin...). As long as you have Python 2.6 or above installed, you can install it with:
```
sudo curl -o /usr/local/bin/dynq -L "https://github.com/rholder/dynq/releases/download/v0.2.0/dynq" && \
sudo chmod +x /usr/local/bin/dynq
```

##Examples
Here's a minimal example of sourcing directly into the current shell from DynamoDB:
```bash
#!/usr/bin/env bash

set -o nounset

# source the content of all of our key/values
source <(dynq --table-name deployment --key-value environment=new_york)

# do something with the variables
echo ${CROSS_STREAMS}
```

Here's a more debuggable example of sourcing some environment variables from
DynamoDB into a temporary file first:

```bash
#!/usr/bin/env bash

set -o nounset

# write out the content of all of our key/values to a tmp file
DYNQ_SOURCE=$(mktemp)
dynq --table-name deployment --key-value environment=new_york > ${DYNQ_SOURCE}

# bring in all of the fetched variables to the current shell
source ${DYNQ_SOURCE}

# do something with the variables
echo ${CROSS_STREAMS}

# clean up when all is well at the end
rm ${DYNQ_SOURCE}
```

##License
The `dynq` project is released under version 2.0 of the
[Apache License](http://www.apache.org/licenses/LICENSE-2.0).

##Contribute
1. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
1. Fork the repository on GitHub to start making your changes to the **master** branch (or branch off of it).
1. Write a test which shows that the bug was fixed or that the feature works as expected.
1. Send a pull request and bug the maintainer until it gets merged and published. :)

##References
* http://aws.amazon.com/dynamodb/
* http://aws.amazon.com/cli/
* http://boto.readthedocs.org/en/latest/