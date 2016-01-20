Clerk
=====

Cisco Inventory Generation
--------------------------

Generates an inventory of specific information regarding Cisco switches from a
folder of text files containing the output of Cisco Show commands.
This information can include, but is not limited to, device hostnames, model
numbers, serial numbers, software image & version and site id's & names. Also
takes into consideration switch stacks as well as individual switches.  This can
then all be collated into a separate text file, csv file or excel spreadsheet,
and updated as necessary if new files are added to the original folder.
Currently, due to the individual nature of device naming conventions and
engineer requirements, this project is not general purpose but built in a
bespoke manner.  The more iterations this tool goes throught the more reusable
it's parts will become.
