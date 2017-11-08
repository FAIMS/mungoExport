# About this exporter:
This exporter was created for the **Mungo Lake Archaeological Survey**, based at La Trobe University, Melbourne, Australia. The module has been documenting the history of human settlement at Lake Mungo, NSW, Australia. The project focuses on the history of human settlement, landscape evolution and past environmental change almost 45,000 years ago.

## Authorship
This exporter was co-developed by Nicola Stern at La Trobe University and Adela Sobotkova and Brian Ballsun-Stanton at the FAIMS Project, Department of Ancient History, Macquarie University.

## Funding:
Development of this module was funded by **ARC LE140100151** aimed to transform digital data collection in archaeology in 2014-2015; MQ Strategic Infrastructure Scheme 20110089, for FAIMS infrastructure development and support in 2016 and MQ Strategic Infrastructure Scheme 20110091, for FAIMS infrastructure development and support in 2017, and **Research Attraction and Acceleration Program (RAAP)** aimed to support innovation and investment in the New South Wales in 2016 and 2017.


## Date of release:
Most recent: June 2017 (previous versions June 2015 & 2016)

## FAIMS Mobile / server version:
FAIMS **v2.5** (Android 6+)

## Licence:
This module is licensed under an international Creative Commons Attribution 4.0 Licence (**CC BY 4.0**).

## Access:
This exporter can be downloaded directly from this repository and used on FAIMS **v2.5** server 
1. Clone the repository
1. Create a tarball (tar.gz) of the repository directory ([Do you know how-to-manage a tarball?](https://faimsproject.atlassian.net/wiki/spaces/MobileUser/pages/54984712/How+to+manage+a+tarball+archive))
1. Upload the tarball to the server through the plugins interface (for details, see below)

## This exporter contains the following features:
* Simplified and custom ordered attributes, without Annotation and Certainty values
* Output Data format: Custom CSV, shapefile, sqlite database, photos with attached metadata 

## Exporter Use Recommendations:
* Immediate field use with [Lake-Mungo Module](https://github.com/FAIMS/Lake-Mungo)

## Contact info:
For more details about the **Lake Mungo Survey** please, contact n.stern@latrobe.edu.au.

If you have any questions about the exporter or the module, please contact the FAIMS team at **enquiries@fedarch.org** and we will get back to you within one business day.

## General How-to Info to Exporters 
[*Based on the 'FAIMS User to Developer Documentation' and 'FAIMS Data UI and Logic Cook Book'*](https://www.fedarch.org/support/#3)

To get the data you have collected with the FAIMS Mobile app in a viewable, usable fashion, you'll need to find and download an exporter. An exporter allows you to export data from FAIMS server in many data formats (CSV, shapefile, sqlite database, json etc.). Each exporter has been customised for individual projects, but with none or minor changes it can be reused for other projects.

**How do I make it work?**
* On a PC, you can simply download / clone the file from GitHub. 

* Create a [tarball](https://faimsproject.atlassian.net/wiki/spaces/MobileUser/pages/54984712/How+to+manage+a+tarball+archive) from the exporter using a program like 7zip; if you're using UNIX, enter something like `tar -czf shapefileExport.tar.gz shapefileExport` 

* Now, if you navigate on the server to your module, you'll see a tab at the top labeled 'Plugin Management'. Click that and you'll be brought to a page with the handy feature, 'Upload Exporter'. Choose the tarball you've just created and hit 'Upload'. You now have an exporter permanently stored to your FAIMS server and may make use of it whenever you'd like.

* From now on, whenever you'd like to use your uploaded exporter, navigate to your module from the main page on the server and click 'Export module'. Select from the dropdown menu the exporter you'd like to use, review and select from any additional options, and click 'Export'.

* You'll be brought to your module's background jobs page while the server exports your data. After a few moments, you should be able to hit 'Refresh' and see a blue hyperlink to 'Export results'. Clicking that will allow you to download your exported data in a compressed file.

**Exporting data doesn't close down the project or prevent you from working any further on it, so feel free to export data whenever it's convenient.**

