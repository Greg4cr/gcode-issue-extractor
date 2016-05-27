# Google Code Issue Extractor
------------------------

Google Code was a hosting service for open-source projects. Each project included an "Issues" page where users could report bugs and request enhancements. In 2016, Google closed the service, but retained issues in a new archived page format (although some information, like the username of the reporter, was discarded).

Prior to closing, the issues page for a project had a CSV download option (for an example, see https://code.google.com/p/android/issues/csv). A large number of scripts used this format to extract information about project issues. After archiving, this option was removed, making it more difficult to perform tasks such as migrate these issues to GitHub. 

This is a Python script to crawl the archived issues page and extract a CSV compatible with the original format. It is relatively basic, extracting the default CSV layout (with dummy values for some fields that were not retained). 

Command Line Parameters
------------------------

In terms of features, this script is fairly basic:

`-p <project name, required>`

This is the project name, as it appears in the URL of Google Code project pages. This is a required field.

`-s <desired statuses, optional comma separated list>`

If you only want to retrieve issues that match a particular status (i.e., "New"), you can specify a set of statuses as a comma separated list (for example, `-s "New,Unassigned"`)

` -l <desired labels, optional  comma separated list>`

Labels can also be filtered (i.e., `-l "Type-Defect"`)

` -o <name of output file`

Name of the CSV file to write to. `<project>-issues.csv` is the default value.

` -q`

"Quiet" mode. Uses PhantomJS as the browser instead of Firefox. This requires that PhantomJS be installed (see below). Useful if script is to be run on a server or other environment where windows cannot be opened. 

If any other features are desired, please file an issue and I'll take a look.

Requirements
------------------------

This script is built using the Selenium Python bindings. If Pip is installed, the Selenium bindings can be installed using `pip install selenium`. 

Selenium requires a web browser to perform page crawling. Firefox is the default. If you want to use this script on a server or an environment where windows cannot be opened, install PhantomJS (http://phantomjs.org/) and change all Firefox references in the script. 

Reporting Faults
------------------------

This script was built quickly to retrieve some information on a particular project, and has not been extensively tested. If you encounter any issues, please file a report, and I'll try to track it down.

