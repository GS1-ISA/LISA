<span style="color:red">**This is an initial release. While we believe it to be robust and correct, at the time of writing (2021-10-15), it has not been rigorously tested and must be used with care**</span>

GS1 Digital Link URI parser
===========================

The GS1 Digital Link URI parser is a simple library for extracting AI element
data from an uncompressed Digital Link URI and presenting it in a number of
formats:

  * Unbracketed element string
  * Bracketed element string
  * JSON

Optionally each representation can be sorted such that the predefined fixed-length AIs appear first.

Optionally the unbracketed representation can have FNC1 separators (represented
by the "^" character) in just the required locations, or as separators for all
AIs.


License
-------

Copyright (c) 2000-2023 GS1 AISBL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this library except in compliance with the License.

You may obtain a copy of the License at:

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.


Documentation
-------------

The interface is straightforward. Refer to the `gs1dlparser.h` header file fpr API documentation and
the `example.c` commandline tool for example use.


### Linux and MacOS

To build the library and run the unit tests:

    make test

To specify a compiler:

    make test CC=clang

To build with runtime analyzers (requires LLVM):

    make test SANITIZE=yes

To fuzz the input to the parser run the following and follow the emitted instructions (requires LLVM libfuzzer):

    make fuzzer

To build and run the example console command:

    make
    ./example-bin 'https://id.gs1.org/01/09520123456788/10/ABC%2F123/21/12345?17=180426'
 
Add `DEBUG=yes` to any of the above to cause the library to emit a detailed trace
of the parse.


### Windows

The Visual Studio solution contains two projects:

  * Unit tests
  * Example console command

Within either of these two projects the `Debug` configuration causes the
library to emit a detailed trace of the parse.


Limitations
-----------

The code implements a lightweight parser that is intended for applications that are subject to infrequent change and must extract AI data from uncompressed Digital Link URIs. The intended purpose is to perform an initial extraction of AI data from a Digital Link URI and present the AI data in common formats for subsequent validation and onwards processing by other code.

It does not embed an AI table since doing so would bloat the code size and require frequent maintenance whenever a new AI is defined.

It does include the list of AIs designated as Digital Link primary keys since this is required to identify the start of AI data in a URI. New keys may be introduced periodically, but not with the same frequency as general AI additions.

As such it has the following limitations:

  * It does not support "compressed" GS1 Digital Link URIs.
  * It does not support the (deprecated) "developer-friendly" AI names feature, e.g. "/gtin/" instead of "/01/".
  * It does not validate the key-qualifier associations (and orderings) with the primary key, nor perform any other form of AI relationship validation that would require a table of AI rules to be incorporated.
  * It does not perform any validation of AI element data; neither whether the AI is assigned, nor whether an AI value follows the rules for the AI.
    * It DOES reject URIs that contain numeric-only components (non-stem path parts or query parameters) that are not 2-4 characters in length that would otherwise be misidentified as an invalid-length AI.
    * It DOES ignore any non-numeric query parameters, as required by the specification.
# moduleCount# VC-Data-Model
This is the repository for discussing and developing GS1's data model as used in Verifiable Credentials.

The data mode document itself is versioned. The latest version is always available at https://ref.gs1.org/gs1/vc/data-model/ with current and previous versions in the [[Archive](https://ref.gs1.org/gs1/vc/data-model/archive)].

The model is supported by a number of ontologies and JSON-LD context files. All assets related to GS1's work on <abbr title="Verifiable Credentials">VC</abbr>s are listed at https://ref.gs1.org/gs1/vc/. The machine-readable files published on ref.gs1.org are snapshots of those developed here. You are welcome to raise and discuss issues here, however, please note the licensing conditions for this repository. Nothing in this work constitutes a GS1 standard and it is not covered by our [IP policy](https://www.gs1.org/standards/ip). Do not contribute any work here over which you may later wish to assert your own IP. Work here is shared publicly and all contributions are themselves public.

All documents in this repository should be considered as suitable for experiments, demos and pilots. At the time of writing, GS1 has not made any commitment to develop and maintain a formal data model. Nevertheless, the existence of these artefacts is a manifestation of a sincere interest in the technology and an expectation of future development.

For questions and further information, contact [Phil Archer](mailto:phil.archer@gs1.org), GS1 Global Office.
GMN JavaScript Helper Library
=============================

This contains an official JavaScript helper library provided by GS1 for check
character pair generation and verification of a Global Model Number (GMN).

It is compatible with all modern web browsers and Node.js 18 or later.


Artifacts
---------

| Asset                 | Purpose                                                            |
| --------------------- | ------------------------------------------------------------------ |
| gmn.js                | The helper library                                                 |
| docs/index.html       | Documentation describing the library's API                         |
| gmn.test.js           | Unit tests for the helper compatible with Jest                     |
| exampleuser.html      | Example code providing a HTML page that uses the library           |
| exampleuser.node.js   | Example code providing a Node.js application that uses the library |


Using the helper library
------------------------

For use within client-side JavaScript of a web page, the gmn.js
file should be copied into your web root and referenced via a HTML script tag:

    <script src="js/gmn.js"></script>

For use within a Node.js application, the gmn.js file can be
referenced via a require statement:

    const GMN = require('./gmn');

Alternatively, you could examine the source code then create your own
specialised implementation. In this case you should apply the unit tests to
your own code as a means of detecting errors.


Documentation
-------------

HTML documentation of the API is included in this distribution: docs/index.html


Running the example web page
----------------------------

Simply open the exampleuser.html file using your JavaScript-enabled web
browser.


Running the example Node.js application
---------------------------------------

From this directory:

    node exampleuser.node.js

When the example application is run without command line arguments it will
display the output of some trivial non-interactive library operations on static
data. It will then enter an interactive mode in which it prompts the user for
an activity to perform and then the data or file to perform the given activity
on.

Additionally, the example application can be called with command line arguments
in which case it will serve as a basic check character pair generation and
verification utility:

    $ node exampleuser.node.js complete 1987654Ad4X4bL5ttr2310c
    1987654Ad4X4bL5ttr2310c2K

    $ node exampleuser.node.js verify 1987654Ad4X4bL5ttr2310c2K
    The check characters are valid

    $ node exampleuser.node.js verify 1987654Ad4X4bL5ttr2310cXX
    The check characters are NOT valid


Running the unit tests
----------------------

If you have modified the helper then you should run the tests using Jest.

From this directory:

    npm install -g jest-cli
    jest


Regenerating the documentation
-------------------------------

Documentation can be regenerated using JSDoc.

From this source directory:

    npm install -g jsdoc
    jsdoc -d docs gmn.js
GMN C# Helper Library
=====================

This contains an official C# helper library provided by GS1 for check character
pair generation and verification of a GS1 Global Model Number (GMN).

Artifacts
---------

| Asset                          | Purpose                                                              |
| ------------------------------ | -------------------------------------------------------------------- |
| GMN.[version].nupkg            | The helper library packaged as a .NET Standard 2.0 NuGet             |
| docs/index.html                | Documentation describing the library's API                           |
| GMN/                           | Source code for the utility class that implements the helper library |
| GMNTests/                      | Unit tests for the utility class compatible with xUnit.NET           |
| ExampleUser/                   | Example code providing a simple application that uses the library    |


Using the helper library
------------------------

The NuGet package can be placed in your local or organisational package
repository and configured as a dependancy of your solution.

Alternatively, the source code for the utility class can be vendored in to your
solution's source code.

Finally, you could examine the source code then create your own specialised
implementation.  In this case you should apply the unit tests to your own code
as a means of detecting errors. The unit tests are generalised to make this
easy provided that you use matching method names.


Documentation
-------------

HTML documentation of the API is included in this distribution: docs/index.html


Building the helper library
---------------------------

This distribution contains a .sln file compatible with Visual Studio 2017 or
later or MSBuild 15 or later.

From this source directory:

    dotnet build GS1GMN.sln

If you have modified the class then you should run the tests using xUnit.NET:

    dotnet test GS1GMN.sln


Running the example application
-------------------------------

From this source directory:

    dotnet publish -o app GS1GMN.sln
    cd app/
    dotnet ExampleUser.dll

When the example application is run without command line arguments it will
display the output of some trivial non-interactive library operations on static
data. It will then enter an interactive mode in which it prompts the user for
an activity to perform and then the data or file to perform the given activity
on.

Additionally, the example application can be called with command line arguments
in which case it will serve as a basic check character pair generation and
verification utility:

    $ dotnet ExampleUser.dll complete 1987654Ad4X4bL5ttr2310c
    1987654Ad4X4bL5ttr2310c2K

    $ dotnet ExampleUser.dll verify 1987654Ad4X4bL5ttr2310c2K
    The check characters are valid

    $ dotnet ExampleUser.dll verify 1987654Ad4X4bL5ttr2310cXX
    The check characters are NOT valid


Recreating the package
----------------------

From this source directory:

    dotnet pack -c Release -o app GMN/GMN.csproj
    cp app/GMN.*.nupkg .


Regenerating the documentation
-------------------------------

Documentation is created as part of a standard build but can be regenerated
specifically.

From this source directory:

    msbuild docfx_project/docfx_project.csproj
GS1 Global Model Number Java Helper Library
===========================================

This contains an official Java helper library provided by GS1 for check
character pair generation and verification of a GS1 Global Model Number (GMN).


Artifacts
---------

| Asset                      | Purpose                                                              |
| -------------------------- | -------------------------------------------------------------------- |
| GMN.jar                    | The helper library packaged as a standard JAR file                   |
| docs/index.html            | Documentation describing the library's API                           |
| org/gs1/GMN.java           | Source code for the utility class that implements the helper library |
| GMNTests.java              | Unit tests for the utility class compatible with JUnit 4 or later    |
| ExampleUser.java           | Example code providing a simple application that uses the library    |


Using the helper library
------------------------

The JAR package can be placed in your local or organisational package
repository and configured as a dependancy of your solution, amending your
classpath as necessary.

Alternatively, the source code for the utility class can be vendored in to your
solution's source code.

Finally, you could examine the source code then create your own specialised
implementation.  In this case you should apply the unit tests to your own code
as a means of detecting errors. The unit tests are generalised to make this
easy provided that you use matching method names.


Documentation
-------------

HTML documentation of the API is included in this distribution at
docs/index.html


Building the helper library
---------------------------

From this source directory:

    javac org/gs1/GMN.java

If you have modified the class then you should run the tests using JUnit 4:

    javac -cp .:[...]/junit4.jar GMNTests.java
    java  -cp .:[...]/junit4.jar org.junit.runner.JUnitCore GMNTests


Building and running the example application
--------------------------------------------

From this source directory:

    javac ExampleUser.java
    java  ExampleUser

Or using the JAR file (Windows):

    javac -cp .;GMN.jar ExampleUser.java
    java  -cp .;GMN.jar ExampleUser

Or using the JAR file (Unix):

    javac -cp .:GMN.jar ExampleUser.java
    java  -cp .:GMN.jar ExampleUser

When the example application is run without command line arguments it will
display the output of some trivial non-interactive library operations on static
data. It will then enter an interactive mode in which it prompts the user for
an activity to perform and then the data or file to perform the given activity
on.

Additionally, the example application can be called with command line arguments
in which case it will serve as a basic check character pair generation and
verification utility:

    $ java ExampleUser complete 1987654Ad4X4bL5ttr2310c
    1987654Ad4X4bL5ttr2310c2K

    $ java ExampleUser verify 1987654Ad4X4bL5ttr2310c2K
    The check characters are valid

    $ java ExampleUser verify 1987654Ad4X4bL5ttr2310cXX
    The check characters are NOT valid


Recreating the JAR package for the library
------------------------------------------

From this source directory:

    javac org/gs1/GMN.java
    jar -cvf GMN.jar org/gs1/*.class


Regenerating the documentation
------------------------------

From this source directory:

    javadoc -d docs org.gs1


Creating a standalone JAR package for the example application
-------------------------------------------------------------

From this source directory:

    javac ExampleUser.java
    jar -cvfm ExampleUser.jar Manifest.txt org/gs1/*.class ExampleUser.class
This directory contains a basic Docker-based build system intended for use by maintainers of the package repository.
GS1 Global Model Number Helper Libraries
========================================

The GS1 GMN Helper Libraries is an open source project that contains a set of
official helper libraries written by GS1 for check character pair generation
and verification of a GS1 Global Model Number (GMN).

**Note**: With the GS1 General Specification Release 21.0 in January 2021, this
library is suitable for all uses of the Global Model Number. This includes use
for Regulated Healthcare medical devices that fall under the EU regulations EU
MDR 2017/745 and EU IVDR 2017/746, specifically when a GMN is used as the
embodiment of a Basic UDI-DI.


Check Character Generation and Validation
-----------------------------------------

The GS1 Global Model Number uses an error detection algorithm that is unlike
other error detection schemes currently in use for GS1 structured data. When
used alongside the GS1 General Specifications these libraries are intended to
simplify adoption of GS1 Global Model Number and to minimise the likelihood of
a flawed implementation of the error detection scheme making it into open use.

The error detection scheme for a GMN is non-trivial: It is the sum of the
products of data character values with decreasing prime weights, modulo a large
prime, with the resulting value being represented by appending two check
characters from an alphanumeric subset of the original data character set
selected by partitioning the value bitwise in two.

This project not only demonstrates clearly how to implement the details of this
algorithm in different well-known programming languages, but each library can
be relied upon as an accurate implementation of the check character pair
generation and validation processes.


Designed for Study
------------------

The libraries are provided in source form which is clearly structured and
descriptively commented enabling developers to research precisely what is
required to create an implementation of the specification with whatever
development platform they are using.

Furthermore, the libraries each include comprehensive unit tests that can be
re-purposed and applied to a specialised implementation to ensure results that
are consistent with a correct implementation of the standard.


Designed for Integration
------------------------

In addition to source form, the libraries are provided in standard packaged
formats, e.g. JAR and NuGet. Either the source can be vendored in to your
application code or the packages can be imported into your development
environment and shipped with your software application, according to preference.

Standard API documentation in HTML format is provided for the public methods
provided by each library.


Batteries Included
------------------

Each library is provided with example source code for an interactive console
application that demonstrates how to correctly call the library functions. These
applications will also accept command line arguments in which case the behave as
a utility that is appropriate for use by sysadmins with only basic scripting
experience.

The examples illustrate how to create and validate the check character pair for
a GMN, whether data is statically coded, supplied interactively or processed by
consuming each line of a file.


Available Libraries
-------------------

The helper libraries are provided in these directories:

| Directory | Purpose                   |
| --------- | ------------------------- |
| java/     | Java helper library       |
| cs/       | C# helper library         |
| js/       | JavaScript helper library |


License
-------

Copyright (c) 2019-2021 GS1 AISBL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this library except in compliance with the License.

You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.


Pedigree
--------

The initial libraries and tests were written (under the commission of GS1 AISBL)
by one of the experts in the technical group that selected the algorithm based
on its performance during the analysis of several alternative schemes under
consideration.
# vbg-l2sd-demo
The [simple demo page](https://gs1.github.io/vbg-l2sd-demo/) shows a Verified by GS1 payload with additional Links to Other Sources of data (L2SD). Just select on eof the available GTINs from the dropdown box and its details should appear.

Alternatively, you can use the [scanner](https://gs1.github.io/vbg-l2sd-demo/vbg-l2sd-camera.html) to scan the UPC/EAN barcode for an item available in the demo. If the scanned item is not available in the demo, you'll see the page exactly as if you had gone straight to it so you can make your selection that way.

Get the scanner on your phone by pointing your phone's camera at this QR code:
	![QR code for https://gs1.github.io/vbg-l2sd-demo/vbg-l2sd-camera.html](cameraQR.png)
# EUDR-tool
A tool for generating European Union Deforestation Regulation notifications using the GS1 Web Vocabulary.
# GS1DigitalLinkToolkit.js
This is a JavaScript toolkit for translating between GS1 element strings and GS1 Digital Link URIs


* [Introduction](#introduction)
* [Overview](#overview)
* [Demo](#demo)
* [Installation](#installation)
* [Basic Usage](#basic-usage)
* [Additional Methods](#additional-methods)
* [Data Resources](#data-resources)
* [Contributors](#contributors)
* [Disclaimer](#disclaimer)
* [Licence](#licence)

## Introduction

The GS1 identification system is widely used worldwide within product barcodes, as well as within barcodes for shipments, assets, locations, etc.

Further information about GS1 can be found at https://www.gs1.org

Details about the GS1 identification system and GS1 Application Identifiers can be found in the GS1 General Specifications at https://www.gs1.org/docs/barcodes/GS1_General_Specifications.pdf and a searchable list of GS1 Application Identifiers is at https://www.gs1.org/standards/barcodes/application-identifiers?lang=en 

GS1 Digital Link is a new Web URI syntax for expressing GS1 Application Identifiers and their values in a Web-friendly format, to make it easier to connect identifiers of products, shipments, locations, assets etc. to related online information and services on the Web via simple Web redirects using Web resolver infrastructure.

The GS1 Digital Link syntax is defined in https://www.gs1.org/standards/Digital-Link/1-0

A demonstration tool is available at https://id.gs1.org/uritool although it does not currently use this toolkit

See also https://github.com/gs1/digital-link.js for a related toolkit for constructing and validating GS1 Digital Link URIs

## Overview

This toolkit provides six translation methods, as indicated in the overview diagram below

![Overview diagram](GS1DigitalLinkToolkitJS-overview.png)

## Demo

A simple interactive demonstration Web page is available at https://gs1.github.io/GS1DigitalLinkToolkit.js/

## Installation

Include the JavaScript file   GS1DigitalLinkToolkit.js   from the source folder /src

e.g.  

```html
<script src="GS1DigitalLinkToolkit.js">
```
  
## Basic Usage

Create a new instance of the GS1DigitalLinkToolkit class as follows:

```js
var gs1dlt = new GS1DigitalLinkToolkit();
```

### Translate GS1 element strings to GS1 Digital Link URI

The method `gs1ElementStringsToGS1DigitalLink(elementStrings, useShortText, uriStem)`
converts a string elementStrings to a GS1 Digital Link URI

The method returns a GS1 Digital Link URI.

elementStrings consists of a single string representing a concatenation of one or more GS1 element strings, either:
- in human-readable format, in which each GS1 Application Identifier is enclosed in round brackets,
  e.g. "(3103)000189(01)05412345000013(3923)2172(10)ABC&+123"
  
- without brackets, in which a group separator character (ASCII character 29 decimal) is used as a delimiter marking the end of any penultimate data value where the corresponding GS1 Application Identifier is not of defined length.

Set the second parameter, `useShortText=true` if you prefer the GS1 Digital Link URI to use alphabetic mnemonic short names as defined in the GS1 Digital Link standard, e.g. /gtin/

Set the second parameter, `useShortText=false` if you prefer the GS1 Digital Link URI to use all-numeric GS1 application identifiers, e.g. /01/

Set the third parameter, `uriStem` to a valid URI stem if you wish to construct a GS1 Digital Link using a specific domain name

If `uriStem` is set to `null`, `undefined` or empty string (''), a default URI stem of 'https://id.gs1.org' will be used.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var elementStrings="(3103)000189(01)05412345000013(3923)2172(10)ABC&+123";
try {
	var gs1DigitalLinkURI = gs1dlt.gs1ElementStringsToGS1DigitalLink(elementStrings, true, 'http://example.org');
	console.log("gs1DigitalLinkURI='"+gs1DigitalLinkURI+"'"); 
	//  gs1DigitalLinkURI='http://example.org/gtin/05412345000013/lot/ABC?3103=000189&3923=2172'
	
} catch(err) {
	console.log(err);
}	
```

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var elementStringsNoBrackets="3103000189010541234500001339232172"+gs1dlt.groupSeparator+"10ABC&+123";
try {
	var gs1DigitalLinkURI = gs1dlt.gs1ElementStringsToGS1DigitalLink(elementStringsNoBrackets, false, null);
	console.log("gs1DigitalLinkURI='"+gs1DigitalLinkURI+"'"); 
	//  gs1DigitalLinkURI='https://id.gs1.org/01/05412345000013/10/ABC%26%2B123?3103=000189&3923=2172'

} catch(err) {
	console.log(err);
}	
```


### Translate GS1 Digital Link URI to GS1 element strings

The method `gs1digitalLinkToGS1elementStrings(gs1DigitalLinkURI,brackets)`
converts a GS1 Digital Link URI to a string representing concatenated GS1 element strings

The first input parameter `gs1DigitalLinkURI` is expected to be a string representation of a valid GS1 Digital Link URI.

This method returns a string value that represents a concatenation of one or more GS1 element strings extracted from the GS1 Digital Link URI that was supplied as input.

Set the second input parameter, `brackets=true` if you require the output element strings expressed in human-readable format, with round brackets around the numeric GS1 Application Identifiers.

Set the second input parameter, `brackets=false` if you do not require human-readable format.  In this situation, a group separator character (ASCII character 29 decimal) will be used as delimiter after the value of any penultimate data element for which the GS1 Application Identifier is not defined to be of fixed length.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1DigitalLinkURI = "http://example.org/gtin/054123450013/lot/ABC%26%2B123?3103=000189&3923=2172";

try {
	var gs1ElementStrings = gs1dlt.gs1digitalLinkToGS1elementStrings(gs1DigitalLinkURI, true);
	console.log("gs1ElementStrings='"+gs1ElementStrings+"'"); 
	//  gs1ElementStrings='(01)00054123450013(10)ABC&+123(3103)000189(3923)2172'
} catch(err) {
	console.log(err);
}	
```

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1DigitalLinkURI = "http://example.org/gtin/054123450013/lot/ABC%26%2B123?3103=000189&3923=2172";

try {
	var gs1ElementStrings = gs1dlt.gs1digitalLinkToGS1elementStrings(gs1DigitalLinkURI, false);
	console.log("gs1ElementStrings='"+gs1ElementStrings+"'"); 
	//  gs1ElementStrings='0100054123450013310300018910ABC&+12339232172' 
} catch(err) {
	console.log(err);
}	
```

## Additional Methods


### Translate GS1 element strings to Associative Array

The method `extractFromGS1elementStrings(elementStrings)`
converts concatenated GS1 element strings to an associative array of GS1 application identifiers and their values. 

The method returns a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

The input parameter `elementStrings` consists of a single string representing a concatenation of one or more GS1 element strings, either:
- in human-readable format, in which each GS1 Application Identifier is enclosed in round brackets,
  e.g. "(3103)000189(01)05412345000013(3923)2172(10)ABC&+123"
  
- without brackets, in which a group separator character (ASCII character 29 decimal) is used as a delimiter marking the end of any penultimate data value where the corresponding GS1 Application Identifier is not of defined length.


```js
var gs1dlt = new GS1DigitalLinkToolkit();

var elementStrings="(3103)000189(01)05412345000013(3923)2172(10)ABC&+123";
try {
	var gs1Array = gs1dlt.extractFromGS1elementStrings(elementStrings);
	console.log("gs1Array="+JSON.stringify(gs1Array)); 
	//  gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"05412345000013"}
	
} catch(err) {
	console.log(err);
}	
```



### Translate Associative Array to GS1 element strings

The method `buildGS1elementStrings(gs1AIarray,brackets)`
converts an associative array of GS1 application identifiers and their values to concatenated GS1 element strings.

This method returns a string value that represents a concatenation of one or more GS1 element strings extracted from the GS1 Digital Link URI that was supplied as input.

The first input parameter, `gs1AIarray` is a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

Set the second input parameter, `brackets=true` if you require the output element strings expressed in human-readable format, with round brackets around the numeric GS1 Application Identifiers.

Set the second input parameter, `brackets=false` if you do not require human-readable format.  In this situation, a group separator character (ASCII character 29 decimal) will be used as delimiter after the value of any penultimate data element for which the GS1 Application Identifier is not defined to be of fixed length.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"00054123450013"};

try {
	var gs1ElementStrings = gs1dlt.buildGS1elementStrings(gs1Array,true);
	console.log("gs1ElementStrings="+gs1ElementStrings); 
	//  gs1ElementStrings=(01)00054123450013(10)ABC&+123(3103)000189(3923)2172
	
} catch(err) {
	console.log(err);
}	
```



### Translate Associative Array to GS1 Digital Link URI

The method `buildGS1digitalLink(gs1AIarray,useShortText,uriStem)`
converts an associative array of GS1 application identifiers and their values to a GS1 Digital Link URI.

The method returns a GS1 Digital Link URI.

The first input parameter, `gs1AIarray` is a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

Set the second parameter, `useShortText=true` if you prefer the GS1 Digital Link URI to use alphabetic mnemonic short names as defined in the GS1 Digital Link standard, e.g. /gtin/

Set the second parameter, `useShortText=false` if you prefer the GS1 Digital Link URI to use all-numeric GS1 application identifiers, e.g. /01/

Set the third parameter, `uriStem` to a valid URI stem if you wish to construct a GS1 Digital Link using a specific domain name

If `uriStem` is set to `null`, `undefined` or empty string (''), a default URI stem of 'https://id.gs1.org' will be used.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"00054123450013"};

try {
	var gs1DigitalLinkURI = gs1dlt.buildGS1digitalLink(gs1Array,true,'https://example.org');
	console.log("gs1DigitalLinkURI="+gs1DigitalLinkURI); 
	//  gs1DigitalLinkURI=https://example.org/gtin/00054123450013/lot/ABC%26%2B123?3103=000189&3923=2172
	
} catch(err) {
	console.log(err);
}	
```



### Translate GS1 Digital Link URI to Associative Array

The method `extractFromGS1digitalLink(gs1DigitalLinkURI)`
converts a GS1 Digital Link URI to an associative array of GS1 application identifiers and their values.

The input parameter `gs1DigitalLinkURI` is expected to be a string representation of a valid GS1 Digital Link URI.

The method returns a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1DigitalLinkURI = "http://example.org/gtin/054123450013/lot/ABC%26%2B123?3103=000189&3923=2172";
try {
	var gs1Array = gs1dlt.extractFromGS1digitalLink(gs1DigitalLinkURI);
	console.log("gs1Array="+JSON.stringify(gs1Array)); 
	//  gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"00054123450013"}
	
} catch(err) {
	console.log(err);
}	
```



## Data resources

The toolkit also provides a number of public data resources which may be useful:

### aitable

returns a list of objects containing information about each GS1 Application Identifier, including:
- title (name) e.g. 'Global Trade Item Number (GTIN)'
- label, e.g. 'GTIN'
- shortcode (as may be used in GS1 Digital Link URI syntax), e.g. 'gtin'
- ai (numeric string equivalent), e.g. '01'
- format (as appearing in the GS1 General Specifications), e.g. 'N14'
- type ("I" = primary identification key, 'Q' = key qualifier, 'D' = data attribute)
- fixedLength (true if appearing in table of defined-length AIs, false otherwise)
- checkDigit (integer indicating check digit position, starting at 1 for first digit - or 'L' for last digit)
- qualifiers (ordered list of numeric AIs for hierarchical sequence of qualifiers, e.g. ["22","10","21"] for GTIN
- regex (regular expression that should match valid values)


### aiCheckDigitPosition

returns an associative array that maps a GS1 Application Identifier to the index (1 = the first digit) for the position of the check digit within GS1 Application Identifiers that have check digits
returns 'L' (last) if the check digit is in the last position
e.g. returns 14 for ITIP, AI (8006)

### aiRegex

returns an associative array that maps a GS1 Application Identifier to a regular expression pattern that should match valid values

### aiMaps

returns an object that contains lists of:
- identifiers
- qualifiers
- dataAttributes
- fixedLength
- variableLength

### aiShortCode

`this.aiShortCode = {"10":"lot","21":"ser","22":"cpv","253":"gdti","254":"glnx","255":"gcn","401":"ginc","402":"gsin","414":"gln","415":"payto","8003":"grai","8004":"giai","8006":"itip","8010":"cpid","8011":"cpsn","8017":"gsrnp","8018":"gsrn","8019":"srin","00":"sscc","01":"gtin"}`

### aiQualifiers

returns an ordered list of GS1 Application Identifiers that are considered as qualifiers for a specific numeric GS1 AI primary identifier

`this.aiQualifiers = {"414":["254"],"8006":["22","10","21"],"8010":["8011"],"8017":["8019"],"8018":["8019"],"01":["22","10","21"]}`

### shortCodeToNumeric

returns an associative array that maps the alphabetic short names that can be used in the GS1 Digital Link to their numeric GS1 Application Identifier counterparts
is the inverse mapping of that provided by aiShortCode (see above)

`this.shortCodeToNumeric = {"lot":"10","ser":"21","cpv":"22","gdti":"253","glnx":"254","gcn":"255","ginc":"401","gsin":"402","gln":"414","payto":"415","grai":"8003","giai":"8004","itip":"8006","cpid":"8010","cpsn":"8011","gsrnp":"8017","gsrn":"8018","srin":"8019","sscc":"00","gtin":"01"}`

### twoDigitAIs

returns a list of two-digit GS1 Application Identifiers

### threeDigitAIs

returns a list of three-digit GS1 Application Identifiers

### fourDigitAIs

returns a list of four-digit GS1 Application Identifiers

### groupSeparator

groupSeparator returns ASCII character 29, 		`this.groupSeparator= String.fromCharCode(29);`


## Contributors  
- Mark Harrison mark.harrison@gs1.org

## Disclaimer  

This is still a pre-alpha release of the software, which still requires further testing.
It is provided on an as-is basis, with no warranty expressed or implied.
Neither GS1 nor the contributors accept any liability for its use nor for any damages caused through its use.

## Licence

Apache-2.0 licence



```
npm install
npm link @transmute/verifiable-credentials
node issue.mjs
# GS1DigitalLicenses

This github repo contains the document development for the simplified GS1 VC Data Model.

View the document [here](https://gs1.github.io/GS1DigitalLicenses/).

# Viewing in web server

Its best to view this in a webserver since content is dynamic. I use

```
python -m http.server 8000
```

# Generation

I used this to build this document

## Install respec for npm

```
npm install -g respec
```

## Generate output html

```
respec index.html -o output.html
```

## Render

```
open output.html
```

## Generate JWTs

To generate the JWT data, first ensure the templates in the ```jsons``` directory are valid and accurate.  Then execute this sequence.
Don't forget to check them in.

```
cd tools
npm install
node issue_go.mjs
node issue_mo.mjs
node issue_mc.mjs
```
# EndToEndTraceability

This public repository is for the development of ideas and open source code for end-to-end traceability of individual objects (such as product instances) within supply chains.  
The draft white paper at [GS1-WhitePaper-VerifiableCredentials-EPCIS-end-to-end-traceability.pdf](https://gs1.github.io/EndToEndTraceability/GS1-WhitePaper-VerifiableCredentials-EPCIS-end-to-end-traceability.pdf) explains some ideas about how a set of EPCIS event data could be sanitised then used within a set of one or more Verifiable Credentials to form a 'proof of connectedness' and to help in establishing trust relationships for sharing visibility data (traceability data) beyond immediate trading partners within a supply chain.  This paper includes ideas developed in earlier GS1 activities such as the former Event-Based Traceability MSWG, as well as more recent developments within GS1 Innovation activities.

## Disclaimer (appearing within the draft white paper)
THIS WHITE PAPER IS PROVIDED “AS IS” WITH NO WARRANTIES WHATSOEVER, INCLUDING ANY WARRANTY OF MERCHANTABILITY, NONINFRINGEMENT, FITNESS FOR PARTICULAR PURPOSE, OR ANY WARRANTY OTHERWISE ARISING OUT OF THIS WHITE PAPER. GS1 disclaims all liability for any damages arising from use or misuse of this White Paper, whether special, indirect, consequential, or compensatory damages, and including liability for infringement of any intellectual property rights, relating to use of information in or reliance upon this document.
GS1 retains the copyright, including the right to make changes to this White Paper at any time, without notice. GS1 makes no warranty for the use of this White Paper and assumes no responsibility for any errors which may appear in the White Paper, nor does it make a commitment to update the information contained herein. GS1 and the GS1 logo are registered trademarks of GS1 AISBL.


# digital-link.js

Javascript library by [Digimarc](https://www.digimarc.com/) for creating, verifying, and representing/transferring
[GS1 Digital Links](https://evrythng.com/news/upgrading-the-barcode-to-the-web-gs1-digital-link/).

This is the library powering the
[GS1 Digital Link Tools](https://digital-link.tools) project,
which allows easy generation and validation of GS1 Digital Links via a UI.

* [Installation](#installation)
* [Usage](#usage)
* [Test App](#test-app)
* [Utilities](#utilities)
* [Unit Tests](#unit-tests)


## Installation

### Node.js or bundler

Install via `npm`:

```bash
$ npm i --save digital-link.js
```

Then `require` it in code:

```js
const { DigitalLink, Utils } = require('digital-link.js');
```


### Script tag

Add a `<script>` tag to your HTML page:

```html
<script src="https://d10ka0m22z5ju5.cloudfront.net/js/digital-link.js/1.3.0/digital-link.js-1.3.0.js"></script>
```

Then access the `digitalLinkJs` global variable:

```js
const { DigitalLink, Utils } = digitalLinkJs;
```


## Usage

The `DigitalLink` object can be created in three ways - with options, using
setters, or an existing URL string. Either method of creation will produce
the same result.


### Create with object

The object can contain the following items:

- `domain` (string) - The domain name of the Digital Link.
- `identifier` (object) - An object containing a single GS1 Application
  Identifier, such as GTIN, as a key-value pair.
- `keyQualifiers` (object) - An object containing one or more GS1 Key Qualifiers
  as key-value pairs.
- `attributes` (object) - As for `keyQualifiers`, but containing GS1 Data
  Attributes and custom extensions supported in the standard as query parameters.
- `sortKeyQualifiers` (boolean) - false by default. If you set it to true, the 
key qualifiers will be sorted in the Web URI String to match the order defined 
by the GS1 Digital Link Grammar.
- `keyQualifiersOrder` (Array) - It's an array that contains all the keys of the 
key qualifiers. If the length of the array is not equal to the length of the
`keyQualifiers` field, this array will be ignored. In this case, the order of the
key qualifier in the Web URI String will be the order of the map.
Otherwise (if the length of the two fields are equal), the order of the key 
qualifier in the Web URI String will be the order define in this field.
- `linkType` - (string) - This optional parameter allows you to request standard 
types of information for a particular Digital Link.

An example is shown below:

```js
const { DigitalLink } = require('digital-link.js');

const dl = DigitalLink({
  domain: 'https://dlnkd.tn.gg',
  identifier: {
    '01': '00860080001300',
  },
  keyQualifiers: {
    '21': '43786',
    '10': '12345'
  },
  keyQualifiersOrder: [
    '10','21'
  ],
  linkType : webVoc.linkType.allergenInfo,
  attributes: {
    thngId: 'UMwxDXBdUbxgtyRaR2HBrc4r',
  },
});
```
Alternatively, you can add the line below to replace the `keyQualifiersOrder`. This will sort them automatically.

```js
sortKeyQualifiers: true
```

### Create with setters

The equivalent to the object-based example above can also be created
piecemeal using setters:

```js
const { DigitalLink } = require('digital-link.js');

const dl = DigitalLink();
dl.setDomain('https://dlnkd.tn.gg');
dl.setIdentifier('01', '00860080001300');
dl.setKeyQualifier('21', '43786');
dl.setKeyQualifier('10', '12345');
dl.setKeyQualifiersOrder(['10', '21']);
dl.setLinkType('gs1:allergenInfo');
dl.setAttribute('thngId', 'UMwxDXBdUbxgtyRaR2HBrc4r');
```

Setters can also be chained:

```js
const { DigitalLink } = require('digital-link.js');

const dl = DigitalLink()
  .setDomain('https://dlnkd.tn.gg')
  .setIdentifier('01', '00860080001300')
  .setKeyQualifier('21', '43786')
  .setKeyQualifier('10', '12345')
  .setKeyQualifiersOrder(['10', '21'])
  .setLinkType('gs1:allergenInfo')
  .setAttribute('thngId', 'UMwxDXBdUbxgtyRaR2HBrc4r');
```


### Create from Web URI aka URL

A `DigitalLink` object can also be created using an existing string:

```js
const uri = 'https://dlnkd.tn.gg/01/00860080001300/10/12345/21/43786?linkType=gs1:allergenInfo';

const dl = DigitalLink(uri);
```


### Web URI and JSON Generation

A `DigitalLink` object can transform itself into a string Web URI (aka URL) representation:

```js
const uri = dl.toWebUriString();

console.log(uri);
```

It is also possible to view the object makeup of the `DigitalLink`. This can
then be used to construct the same `DigitalLink` from an object.

```js
// Get JSON representation
const jsonString = dl.toJsonString();
console.log(jsonString);

// Create DigitalLink using same data
const dl2 = DigitalLink(JSON.parse(jsonString));
```

### Link Types - `linkType`

The SDK supports the GS1 Digital Link `linkType` feature. Link types allow applications to request specific information for a given product. For instance an application could request allergen information for a given GTIN by adding the link type `linkType=gs1:allergenInfo`. Supported standard link types are specified in the [GS1 Web Vocabulary](https://www.gs1.org/voc/) and additionally you can define your own types.

`setLinkType` and `getLinkType` allow specifying respectively reading a link type. On top of this the SDK provides a convenient list of all supported standard link types. To use it simply import `webVoc` as shown below:

```js
const { DigitalLink, webVoc } = require('digital-link.js');
dl.setLinkType(webVoc.linkType.allergenInfo);
```

### Digital Link Validation

Once created, the `DigitalLink` object can validate itself:

```js
const isValid = dl.isValid();

console.log(`Is the Digital Link valid? ${isValid}`);
```

You can also view the validation trace output at each match stage. Any remainder
after the last stage can be deemed erroneous, as it did not match any rule in
the grammar:

```js
const dl = DigitalLink('https://gs1.evrythng.com/01/9780345418913x');
const trace = dl.getValidationTrace();

console.log(trace);
```

The example above contains an erroneous 'x' at the end, so it does not validate:

```json
{
  "trace": [
    { "rule": "scheme", "match": "https", "remainder": "://gs1.evrythng.com/01/9780345418913x" },
    { "rule": "reg-name", "match": "gs1.evrythng.com", "remainder": "/01/9780345418913x" },
    { "rule": "host", "match": "gs1.evrythng.com", "remainder": "/01/9780345418913x" },
    { "rule": "hostname", "match": "gs1.evrythng.com", "remainder": "/01/9780345418913x" },
    { "rule": "customURIstem", "match": "https://gs1.evrythng.com", "remainder": "/01/9780345418913x" },
    { "rule": "gtin-code", "match": "01", "remainder": "/9780345418913x" },
    { "rule": "gtin-value", "match": "9780345418913", "remainder": "x" },
    { "rule": "gtin-comp", "match": "/01/9780345418913", "remainder": "x" },
    { "rule": "gtin-path", "match": "/01/9780345418913", "remainder": "x" },
    { "rule": "gs1path", "match": "/01/9780345418913", "remainder": "x" },
    { "rule": "gs1uriPattern", "match": "/01/9780345418913", "remainder": "x" },
    { "rule": "customGS1webURI", "match": "https://gs1.evrythng.com/01/9780345418913", "remainder": "x" }
  ],
  "success": false
}
```
> Warning : if your domain contains a custom path (for example : `https://example.com/custom/path/01/00860080001300`), 
> It will be removed (`https://example.com/01/00860080001300`) in the validation trace. That's because the
> Digital Link Grammar file doesn't support the custom paths.

> Warning : The isValid method also checks if the identifier has a valid check digit. If it isn't the case, it will 
> return false. However, the getValidationTrace won't show any error since it doesn't take into account the check digit
> verification.

### Compression

The GS1 Digital Link standard also describes an (offline) 
compression/decompression mechanism that allows for shorter URLs and 
hence unlocks use cases where the size of the data carrier (e.g., QR code) is
very limited.

To create a compressed URI, use the `toCompressedWebUriString()` method:

```js
const uri = 'https://dlnkd.tn.gg/01/00860080001300/21/43786';
const dl = DigitalLink(uri);

const compressedUri = dl.toCompressedWebUriString();
```

To attempt decompression of a compressed URI use the constructor function as
usual:

```js
const compressedUri = 'https://dlnkd.tn.gg/DBHKVAdpQgqrCg';

const dl = DigitalLink(compressedUri);
```

> Note: decompression will fail if the result is not a valid GS1 Digital Link.

The `Utils` object also provides methods for direct compression and
decompression of URI strings:

```js
const { Utils } = require('digital-link.js');

const uri = 'https://dlnkd.tn.gg/01/00860080001300/21/43786';

// Compress a URI
const compressedUri = Utils.compressWebUri(uri);

// Compress without optimisations or compressing other key-value pairs
const useOptimisations = false;
const compressOtherKeyValuePairs = false;
const semiCompressedUri = Utils.compressWebUri(uri, useOptimisations, compressOtherKeyValuePairs);

// Decompress a compressed URI
const decompressedUri = Utils.decompressWebUri(compressedUri);

// Detect if a URI is compressed
const isCompressed = Utils.isCompressedWebUri(compressedUri);
```


## Test App

![](test-app/assets/screenshot.png)

The `test-app` directory contains a simple app built with
[Hyperapp](https://github.com/jorgebucaran/hyperapp) that demonstrates how to
easily build a simple GS1 Digital Link verification tool using this SDK.

To use it:

1. `cd test-app && npm i`
2. `npm run serve`
3. Open `http://localhost:1234/index.html` in a browser of choice.
4. Enter or type a GS1 Digital Link, and observe the validity.

The trace steps (which matched a parser rule) are also shown, allowing you to
see which parts of your input did not match any rule. The output of
`toJsonString()` is also shown as an insight into the make-up of the URL itself.

## Utilities

Since this library is based on
[`apglib`](https://github.com/ldthomas/apg-js2-lib), it can do more than simply
validate GS1 Digital Link URLs. The `Utils` object allows a single Application
Identifier to be validated (as well as a whole canonical URL). All available
individual rules are available from the `Rules` object

For example, validating a GTIN by itself:

```js
const { Utils } = require('digital-link.js');

// Validate a GTIN
const gtin = '00860080001300';
const rule = Utils.Rules.gtin;

console.log(`Is the GTIN ${gtin} valid? ${Util.testRule(rule, gtin)}`);
```

It also allows generation of simple HTML tables that detail the results of the
parser run against the input:

```js
const { DigitalLink, Utils } = require('digital-link.js');

const dl = DigitalLink('https://gs1.evrythng.com/01/00860080001300');

// See all the parser trace steps for a given DigitalLink URL
traceSpan.innerHTML = Utils.generateTraceHtml(dl.toUrlString());

// See all the parser stats for a given DigitalLink URL
statsSpan.innerHTML = Utils.generateStatsHtml(dl.toUrlString());

// See all the parser results for a given DigitalLink URL
resultsSpan.innerHTML = Utils.generateResultsHtml(dl.toUrlString());
```

> Warning : if your domain contains a custom path (for example : `https://example.com/custom/path/01/00860080001300`), 
> We recommand you to remove it (`https://example.com/01/00860080001300`) by calling `Utils.removeCustomPath()` for the 
> `generateTraceHtml`, `generateStatsHtml` and `generateResultsHtml` functions. Since the Digital Link Grammar 
> file doesn't support the custom path. Otherwise, all your fields (identifier, key qualifiers, ...) won't be
> recognized.

### ABNF Grammar

The generation of this tool is based on the standard's ABNF grammar.
The grammar files corresponding to each version of the standard can be found in
the `grammar` folder.

## Unit Tests

Unit tests can be run with the `npm test` command, and cover all methods,
creation methods, and output formats.

## Third party libraries

`digital-link.js` was built using some great third party libraries, in
particular:

* [`apglib`](https://github.com/ldthomas/apg-js2-lib) - which is used to verify
  links based on the standard `ABNF` grammar.
* [`GS1DigitalLinkCompressionPrototype`](https://github.com/gs1/GS1DigitalLinkCompressionPrototype) -
  which is a prototype implementation of the Digital Link compression as
  specified in the GS1 Digital Link 1.1 draft specification.

## Deployment

See `jenkins` for deployment instructions.
# Example GTIN
The landing page for the example GTIN 09506000149301
GS1 Barcode Syntax Dictionary and Syntax Tests
==============================================

The **GS1 Barcode Syntax Dictionary** ("Syntax Dictionary") is a text file that is both human-readable and
machine-readable, which consists of a set of entries describing each currently
assigned GS1 Application Identifier in terms of its constituent components.

The current revision of the Syntax Dictionary can be viewed and downloaded
from here:

<https://ref.gs1.org/tools/gs1-barcode-syntax-resource/syntax-dictionary/>

The contents of the dictionary are intentionally straightforward, however it is
sufficient to facilitate certain activities that are essential for processing
GS1 Application Identifier and GS1 Digital Link data, chiefly:

  * Accurately convert between the various different representations of GS1 Application Identifier syntax data.
    * Bracketed and unbracketed format
    * Barcode message scan data
    * HRI and non-HRI text
    * GS1 Digital Link URIs
  * Validate Application Identifier associations, in particular mutually-exclusive AIs and requisite AIs.

The **GS1 Barcode Syntax Tests** ("Linters") are referred to by the
AI entries within the Syntax Dictionary, and enable the user to perform
validation of the syntax of the content for AI-based messages such as AI
element strings and GS1 Digital Link URIs. Reference implementations of the
routines are provided in the C language.

The Syntax Dictionary, together with the Linters, can either be used directly
or transliterated into third-party code. It is intended that it should be
straightforward for projects that adopt these resources to update to new
revisions whenever there are changes to the Syntax Dictionary and new Linters
in response to updates in the corresponding specifications.

Further details about the activities and motivation for the Syntax Dictionary
are given in the following article:

<https://www.linkedin.com/pulse/gs1-application-identifier-syntax-dictionary-terry-burton/>

This repository contains the following key artifacts:

| Artifact                    | Purpose                                                                                                              |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `gs1-syntax-dictionary.txt` | The Syntax Dictionary                                                                                                |
| `src/lint_<name>.c`         | Source for the reference Linters, which includes unit tests                                                          |
| `src/gs1syntaxdictionary.h` | Headers file with Linter function declarations and Linter error code definitions                                     |
| `src/gs1syntaxdictionary.c` | Optional implementations for mapping Linter names to functions and Linter error codes to error message strings       |
| `docs/`                     | Linter function descriptions in HTML format                                                                          |


Documentation
-------------

The structure of the Syntax Dictionary is defined in detail by its introductory comments.

The reference Linters are extensively documented in the code, with the documentation being
made available online here:

<https://ref.gs1.org/tools/gs1-barcode-syntax-resource/syntax-tests/>


Using the Syntax Dictionary and Linters
---------------------------------------

The software license for this project is permissive allowing for the source code to be vendored into a
codebase (Open Source or proprietary) and compiled into an application, or for a
pre-built shared library of Linter routines to be redistributed (either
alongside a third-party application or provided separately) and dynamically loaded at
runtime.

Applications that wish to implement the Syntax Dictionary and Linters must
provide the necessary framework code. This includes parsing the Syntax
Dictionary to initialise any internal data structures, then using the
extracted rules to validate and transform AI-based messages such as AI element
strings or GS1 Digital Link URIs.

For example, depending on the requirements of the application it may need to:

  * Apply the format specification rules for AIs to separate the AI element string or GS1 Digital Link URI message into distinct AIs, e.g. using FNC1 separators or predefined fixed-length.
  * Separate AIs into parts based on their components' designated length.
  * Apply the format specification and Linters (or a port / translation of them) to the AI components to validate their contents.
  * Apply the AI association rules over the entirety of the AI data to validate exclusive and mandatory AI pairings and/or GS1 Digital Link path primary-key to key-qualifier associations.
  * Construct valid GS1 barcode message data (i.e. with FNC1 in first), bracketed/unbracketed element strings, HRI/non-HRI text, and GS1 Digital Link URIs based on the AI component format specifications and AI associations.

The **GS1 Syntax Engine** is a library that provides one such framework
implementation of the Syntax Dictionary and Linters, and serves as an example
of how to use this project effectively:

<https://ref.gs1.org/tools/gs1-barcode-syntax-resource/syntax-engine/>

The GS1 Syntax Engine builds the Linter routines into its library code and
demonstrates two distinct approaches to integrating with the Syntax Dictionary:
(1) Processing the Syntax Dictionary to dynamically populate internal data
structures during application startup; (2) embedding a static table of data
derived from the Syntax Dictionary during the application build process, that
is used as a fallback if the Syntax Dictionary file is not available.

Either of these approaches may be used to enhance the capabilities of an
application to facilitate transformation and validation of GS1 AI-based data.

Alternatively developers may choose to program their application to use the
Syntax Engine library directly (by vendoring in the source or linking the C
library, possibly using one of the language bindings) to entirely avoid
implementing the Syntax Dictionary and Linter framework themselves.


### Building the Linters on Windows

The Linters can be rebuilt on Windows using MSVC.

The project contains a solution file (.sln) compatible with recent versions of
Microsoft Visual Studio. In the Visual Studio Installer you will need to ensure
that MSVC is installed by selecting the "C++ workload".

Alternatively, they can be built from the command line by opening a
Developer Command Prompt, cloning this repository, changing to the `src`
directory and building the solution using:

    msbuild /p:Configuration=release gs1syntaxdictionary.sln

Or:

    msbuild /p:Configuration=debug gs1syntaxdictionary.sln


### Building the Linters on Linux or MacOS

The Linters can be rebuilt on any Linux or MacOS system that has a C compiler
(such as GCC or Clang).

To build using the default compiler change into the `src` directory and run:

    make

A specific compiler can be chosen by setting the CC argument for example:

    make CC=gcc

    make CC=clang

There are a number of other targets that are useful for development purposes:

    make test [SANITIZE=yes]  # Run the unit test suite, optionally building using LLVM sanitizers
    make fuzzer               # Build fuzzers for exercising the individual Linters. Requires LLVM libfuzzer.

# TDT

Demo web interface implementation of [TDS 2.2](https://ref.gs1.org/standards/tds/2.2.0/) and [TDT 2.2](https://ref.gs1.org/standards/tdt/2.2.0/) , using the [TDT 2.2 translation files](https://ref.gs1.org/standards/tdt/artefacts).

[Online demo tool available here](https://gs1.github.io/TDT/demo/)
# 2d-barcode-demonstrator
A tool for generating 2D barcodes with AI syntax and GS1 Digital Link URIs.

This is for demo use only and **not** to be used to generate barcodes for use on actual products. It exists primarily to show the different syntaxes defined in the GS1 system and how these are independent of the choice of data carrier.

A [demo](https://gs1.github.io/2d-barcode-generator/) is available.
# UnitConverterUNECERec20
Javascript library for converting quantitative values expressed using UN ECE Recommendation 20 unit codes

## Online demonstation

https://gs1.github.io/UnitConverterUNECERec20/

## Installation

Include the JavaScript file   UnitConverterUNECERec20.js   from the source folder /src

e.g.  

```html
<script src="UnitConverterUNECERec20.js">
```
  
## Basic Usage

Create a new instance of the UnitConverterUNECERec20.js class as follows:

```js
var units=new UnitConverterUNECERec20();
```

## Convert quantitative value from one unit of measure to a different specified unit

```js
var units=new UnitConverterUNECERec20();

var result=convert({"FAH",212},"CEL");

// convert 212 degrees Fahrenheit to degrees Celsius gives result=100
```

## Find related units for the same physical property

```js
var units=new UnitConverterUNECERec20();

var relatedUnits=relatedUnits("ATM");

// find related units for "ATM" (atmospheres) 
// returns other units of pressure, ["ATM","BAR","HN","J89","MBR","PAL","PS"]
```

## Convert quantitative value from one unit of measure to multiple units of the same physical property

```js
var units=new UnitConverterUNECERec20();

var result=multiconvert({"CEL",100});

// convert 100 degrees Celsius into other temperature units 
// result:  {"KEL":373.15,"FAH":211.99999999999997,"CEL":100,"A48":671.67}
```


# vc-data-model-verifier
Code for verifying that the payload of a VC issued by GS1 conforms to the published data model
# Interpret GS1 scan

<p>Interpret GS1 scan is a JavaScript library that interprets a given string of data as its constituent GS1 application identifiers and their values. It accepts AI syntax, both human readable and using FNC1, as well as GS1 Digital Link URIs. The primary use case is the interpretation of a string captured by scanning a barcode.</p>
 
 # Dependency

<p>Interpret GS1 scan depends on the <a href="https://github.com/gs1/GS1DigitalLinkToolkit.js">GS1 Digital Link toolkit</a> and the <a href="plausibleGS1DL.js">plausibleGS1DL.js</a> function. The latter includes ample documentation within the code itself and exists to provide a simple way to
determine whether a given string plausibly is, or definitely is not, a GS1 Digital Link URI.</p>

# The Interpret Scan function

<p>If there are no errors, the <code>interpretScan()</code> function returns an object as follows</p><ul>
 <li><code>AIbrackets</code>: The equivalent GS1 element string in human-readable AI syntax</li>
<li><code>AIfnc1</code>: The equivalent GS1 element string in AI syntax with FNC1 (as used in barcodes)</li>
 <li><code>dl</code>: The equivalent GS1 Digital Link URL (on id.gs1.org)</li>
<li><code>ol</code>: An ordered array of objects parsed/interpreted from the input string:<ul>
 <li><code>ai</code>: the GS1 Application Identifier</li>
 <li><code>label</code>: what that AI is used for</li>
  <li><code>value</code>: the value</li></ul></li></ul>
 <p>The order for the <code>ol</code> list matches that found in a GS1 Digital Link URI</p><ol>
 <li>primary identifier</li>
 <li>any applicable qualifiers</li>
 <li>any data attributes</li>
 <li>any non-GS1 AIs and their values</li></ol>
 <p>Simply pass the string to be interpreted to the `interpretScan()` function.</p>
 <p>It can handle any of the 3 formats as input:</p><ul>
 <li>Human readable AI syntax (i.e. with brackets)</li>
 <li>Pure AI syntax (i.e. with the FNC1 character)</li>
 <li>GS1 Digital Link URI</li></ul>
<p>If the input string cannot be interpreted, i.e. it's not a valid GS1 string, then the returned object has a value for <code>errmsg</code> which is the system error message.</p>

# Display interpretation

<p>A second function, <code>displayInterpretation()</code> takes two parameters: the string (which it passes to <code>interpretScan()</code>) and the element in an HTML page to which it can write its interpretation (as a number of DOM elements).</p>

<p>A basic <a href="https://gs1.github.io/interpretGS1scan/">demo is available</a>.</p>

# Scanner demo

<p>You might want to head over to the <a href="https://gs1.github.io/interpretGS1scan/camera.html">scanner demo</a>.</p>
<img src="demoQR.gif" alt="QR code for https://gs1.github.io/interpretGS1scan/camera.html" style="width:116px; margin:0 auto; display:block; margin: 1em" />
<p>Sadly, <strong>this demo does not work in all browsers</strong>. It seems to work well with:</p><ul>
 <li>Samsung Internet on Android</li>
 <li>Chrome on Android</li></ul>
 <p>It is usable but without the beep or choice of camera when used with Safari on iOS</p>
 <p>It does not work with Chrome on iOS</p>
 <p>It does not work with Firefox on Windows</p>
 <p>We'll do what we can to improve this but a lot of it is down to the underlying libraries and the variance in implementation of the camera API across browsers and platforms.</p>

# Dal Giardino
A repository for the fictitious brand, used for GS1 Digital Link demos. It is *not* a website in the usual sense, however, the [index page](https://gs1.github.io/dalgiardino/) is a useful jumping off point.

Please note that this repo includes licensed images that may not be used elsewhere, unless otherwise stated.
# GS1DigitalLinkCompressionPrototype
This is a JavaScript toolkit for translating between GS1 element strings and GS1 Digital Link URIs. It includes reversible compression functions, as defined in the [GS1 Digital Link standard](https://www.gs1.org/standards/gs1-digital-link). Please note the [legal disclaimer](https://ref.gs1.org/gs1/standards-disclaimer/) that applies to all GS1 standards.


* [Introduction and status](#introduction)
* [Overview](#overview)
* [Installation](#installation)
* [Basic Usage](#basic-usage)
* [Additional Methods](#additional-methods)
* [Data Resources](#data-resources)
* [Contributors](#contributors)
* [Disclaimer](#disclaimer)
* [Licence](#licence)

## Introduction and status

The [GS1](https://www.gs1.org) identification system is widely used worldwide within product barcodes, as well as within barcodes for shipments, assets, locations, etc.

Details about the GS1 identification system and GS1 Application Identifiers can be found in the GS1 General Specifications at https://www.gs1.org/docs/barcodes/GS1_General_Specifications.pdf and a searchable list of GS1 Application Identifiers is at https://www.gs1.org/standards/barcodes/application-identifiers?lang=en 

GS1 Digital Link is a Web URI syntax for expressing GS1 Application Identifiers and their values in a Web-friendly format, to make it easier to connect identifiers of products, shipments, locations, assets etc. to related online information and services on the Web via simple Web redirects using Web resolver infrastructure.

The syntax is part of the [GS1 Digital Link standard](https://www.gs1.org/standards/Digital-Link)

The library in this repository was developed alongside the compression/decompression alogorithm defined in that standard. At the time, it was considered experimental and was therefore not included in the [GS1 Digital Link toolkit](https://github.com/gs1/GS1DigitalLinkToolkit.js). Since then, the algorithm has been confirmed (with slight additions in version 1.2 of the standard), and a couple of minor bugs have been found (and corrected). 

A near-future task is to combine this library with the GS1 Digital Link toolkit and to modularize everything so you can just import the code for the functions you need.

Looking for an alternative implementation? See the [Trust Codes compression/decompression](https://github.com/TrustCodes/gs1-compression) Python library.

## Overview

This extended version of the toolkit provides ten translation methods, as indicated in the overview diagram below

![Overview diagram](GS1DigitalLinkToolkitJSoverview_compressed2.png)


## Installation

Include the JavaScript file   GS1DigitalLinkToolkit.js   from the source folder /src

e.g.  

```html
<script src="GS1DigitalLinkToolkit.js">
```
  
## Basic Usage

Create a new instance of the GS1DigitalLinkToolkit class as follows:

```js
var gs1dlt = new GS1DigitalLinkToolkit();
```

### Translate GS1 element strings to GS1 Digital Link URI

The method `gs1ElementStringsToGS1DigitalLink(elementStrings, useShortText, uriStem)`
converts a string elementStrings to a GS1 Digital Link URI

The method returns a GS1 Digital Link URI.

elementStrings consists of a single string representing a concatenation of one or more GS1 element strings, either:
- in human-readable format, in which each GS1 Application Identifier is enclosed in round brackets,
  e.g. "(3103)000189(01)05412345000013(3923)2172(10)ABC&+123"
  
- without brackets, in which a group separator character (ASCII character 29 decimal) is used as a delimiter marking the end of any penultimate data value where the corresponding GS1 Application Identifier is not of defined length.

Set the second parameter, `useShortText=true` if you prefer the GS1 Digital Link URI to use alphabetic mnemonic short names as defined in the GS1 Digital Link standard, e.g. /gtin/

Set the second parameter, `useShortText=false` if you prefer the GS1 Digital Link URI to use all-numeric GS1 application identifiers, e.g. /01/

Set the third parameter, `uriStem` to a valid URI stem if you wish to construct a GS1 Digital Link using a specific domain name

If `uriStem` is set to `null`, `undefined` or empty string (''), a default URI stem of 'https://id.gs1.org' will be used.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var elementStrings="(3103)000189(01)05412345000013(3923)2172(10)ABC&+123";
try {
	var gs1DigitalLinkURI = gs1dlt.gs1ElementStringsToGS1DigitalLink(elementStrings, true, 'http://example.org');
	console.log("gs1DigitalLinkURI='"+gs1DigitalLinkURI+"'"); 
	//  gs1DigitalLinkURI='http://example.org/gtin/05412345000013/lot/ABC?3103=000189&3923=2172'
	
} catch(err) {
	console.log(err);
}	
```

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var elementStringsNoBrackets="3103000189010541234500001339232172"+gs1dlt.groupSeparator+"10ABC&+123";
try {
	var gs1DigitalLinkURI = gs1dlt.gs1ElementStringsToGS1DigitalLink(elementStringsNoBrackets, false, null);
	console.log("gs1DigitalLinkURI='"+gs1DigitalLinkURI+"'"); 
	//  gs1DigitalLinkURI='https://id.gs1.org/01/05412345000013/10/ABC%26%2B123?3103=000189&3923=2172'

} catch(err) {
	console.log(err);
}	
```


### Translate GS1 Digital Link URI to GS1 element strings

The method `gs1digitalLinkToGS1elementStrings(gs1DigitalLinkURI,brackets)`
converts a GS1 Digital Link URI to a string representing concatenated GS1 element strings

The first input parameter `gs1DigitalLinkURI` is expected to be a string representation of a valid GS1 Digital Link URI.

This method returns a string value that represents a concatenation of one or more GS1 element strings extracted from the GS1 Digital Link URI that was supplied as input.

Set the second input parameter, `brackets=true` if you require the output element strings expressed in human-readable format, with round brackets around the numeric GS1 Application Identifiers.

Set the second input parameter, `brackets=false` if you do not require human-readable format.  In this situation, a group separator character (ASCII character 29 decimal) will be used as delimiter after the value of any penultimate data element for which the GS1 Application Identifier is not defined to be of fixed length.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1DigitalLinkURI = "http://example.org/gtin/054123450013/lot/ABC%26%2B123?3103=000189&3923=2172";

try {
	var gs1ElementStrings = gs1dlt.gs1digitalLinkToGS1elementStrings(gs1DigitalLinkURI, true);
	console.log("gs1ElementStrings='"+gs1ElementStrings+"'"); 
	//  gs1ElementStrings='(01)00054123450013(10)ABC&+123(3103)000189(3923)2172'
} catch(err) {
	console.log(err);
}	
```

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1DigitalLinkURI = "http://example.org/gtin/054123450013/lot/ABC%26%2B123?3103=000189&3923=2172";

try {
	var gs1ElementStrings = gs1dlt.gs1digitalLinkToGS1elementStrings(gs1DigitalLinkURI, false);
	console.log("gs1ElementStrings='"+gs1ElementStrings+"'"); 
	//  gs1ElementStrings='0100054123450013310300018910ABC&+12339232172' 
} catch(err) {
	console.log(err);
}	
```

## Additional Methods


### Translate GS1 element strings to Associative Array

The method `extractFromGS1elementStrings(elementStrings)`
converts concatenated GS1 element strings to an associative array of GS1 application identifiers and their values. 

The method returns a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

The input parameter `elementStrings` consists of a single string representing a concatenation of one or more GS1 element strings, either:
- in human-readable format, in which each GS1 Application Identifier is enclosed in round brackets,
  e.g. "(3103)000189(01)05412345000013(3923)2172(10)ABC&+123"
  
- without brackets, in which a group separator character (ASCII character 29 decimal) is used as a delimiter marking the end of any penultimate data value where the corresponding GS1 Application Identifier is not of defined length.


```js
var gs1dlt = new GS1DigitalLinkToolkit();

var elementStrings="(3103)000189(01)05412345000013(3923)2172(10)ABC&+123";
try {
	var gs1Array = gs1dlt.extractFromGS1elementStrings(elementStrings);
	console.log("gs1Array="+JSON.stringify(gs1Array)); 
	//  gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"05412345000013"}
	
} catch(err) {
	console.log(err);
}	
```



### Translate Associative Array to GS1 element strings

The method `buildGS1elementStrings(gs1AIarray,brackets)`
converts an associative array of GS1 application identifiers and their values to concatenated GS1 element strings.

This method returns a string value that represents a concatenation of one or more GS1 element strings extracted from the GS1 Digital Link URI that was supplied as input.

The first input parameter, `gs1AIarray` is a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

Set the second input parameter, `brackets=true` if you require the output element strings expressed in human-readable format, with round brackets around the numeric GS1 Application Identifiers.

Set the second input parameter, `brackets=false` if you do not require human-readable format.  In this situation, a group separator character (ASCII character 29 decimal) will be used as delimiter after the value of any penultimate data element for which the GS1 Application Identifier is not defined to be of fixed length.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"00054123450013"};

try {
	var gs1ElementStrings = gs1dlt.buildGS1elementStrings(gs1Array,true);
	console.log("gs1ElementStrings="+gs1ElementStrings); 
	//  gs1ElementStrings=(01)00054123450013(10)ABC&+123(3103)000189(3923)2172
	
} catch(err) {
	console.log(err);
}	
```



### Translate Associative Array to GS1 Digital Link URI

The method `buildGS1digitalLink(gs1AIarray,useShortText,uriStem)`
converts an associative array of GS1 application identifiers and their values to a GS1 Digital Link URI.

The method returns a GS1 Digital Link URI.

The first input parameter, `gs1AIarray` is a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

Set the second parameter, `useShortText=true` if you prefer the GS1 Digital Link URI to use alphabetic mnemonic short names as defined in the GS1 Digital Link standard, e.g. /gtin/

Set the second parameter, `useShortText=false` if you prefer the GS1 Digital Link URI to use all-numeric GS1 application identifiers, e.g. /01/

Set the third parameter, `uriStem` to a valid URI stem if you wish to construct a GS1 Digital Link using a specific domain name

If `uriStem` is set to `null`, `undefined` or empty string (''), a default URI stem of 'https://id.gs1.org' will be used.

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"00054123450013"};

try {
	var gs1DigitalLinkURI = gs1dlt.buildGS1digitalLink(gs1Array,true,'https://example.org');
	console.log("gs1DigitalLinkURI="+gs1DigitalLinkURI); 
	//  gs1DigitalLinkURI=https://example.org/gtin/00054123450013/lot/ABC%26%2B123?3103=000189&3923=2172
	
} catch(err) {
	console.log(err);
}	
```



### Translate GS1 Digital Link URI to Associative Array

The method `extractFromGS1digitalLink(gs1DigitalLinkURI)`
converts a GS1 Digital Link URI to an associative array of GS1 application identifiers and their values.

The input parameter `gs1DigitalLinkURI` is expected to be a string representation of a valid GS1 Digital Link URI.

The method returns a JavaScript object containing numeric GS1 Application Identifier keys and their corresponding values, e.g. {"01":"05412345000013","10":"ABC&+123"}

```js
var gs1dlt = new GS1DigitalLinkToolkit();

var gs1DigitalLinkURI = "http://example.org/gtin/054123450013/lot/ABC%26%2B123?3103=000189&3923=2172";
try {
	var gs1Array = gs1dlt.extractFromGS1digitalLink(gs1DigitalLinkURI);
	console.log("gs1Array="+JSON.stringify(gs1Array)); 
	//  gs1Array={"10":"ABC&+123","3103":"000189","3923":"2172","01":"00054123450013"}
	
} catch(err) {
	console.log(err);
}	
```



## Data resources

The toolkit also provides a number of public data resources which may be useful:

### aitable

returns a list of objects containing information about each GS1 Application Identifier, including:
- title (name) e.g. 'Global Trade Item Number (GTIN)'
- label, e.g. 'GTIN'
- shortcode (as may be used in GS1 Digital Link URI syntax), e.g. 'gtin'
- ai (numeric string equivalent), e.g. '01'
- format (as appearing in the GS1 General Specifications), e.g. 'N14'
- type ("I" = primary identification key, 'Q' = key qualifier, 'D' = data attribute)
- fixedLength (true if appearing in table of defined-length AIs, false otherwise)
- checkDigit (integer indicating check digit position, starting at 1 for first digit - or 'L' for last digit)
- qualifiers (ordered list of numeric AIs for hierarchical sequence of qualifiers, e.g. ["22","10","21"] for GTIN
- regex (regular expression that should match valid values)


### aiCheckDigitPosition

returns an associative array that maps a GS1 Application Identifier to the index (1 = the first digit) for the position of the check digit within GS1 Application Identifiers that have check digits
returns 'L' (last) if the check digit is in the last position

### aiRegex

returns an associative array that maps a GS1 Application Identifier to a regular expression pattern that should match valid values

### aiMaps

returns an object that contains lists of:
- identifiers
- qualifiers
- dataAttributes
- fixedLength
- variableLength

### aiShortCode

`this.aiShortCode = {"10":"lot","21":"ser","22":"cpv","253":"gdti","254":"glnx","255":"gcn","401":"ginc","402":"gsin","414":"gln","415":"payto","8003":"grai","8004":"giai","8006":"itip","8010":"cpid","8011":"cpsn","8017":"gsrnp","8018":"gsrn","8019":"srin","00":"sscc","01":"gtin"}`

### aiQualifiers

returns an ordered list of GS1 Application Identifiers that are considered as qualifiers for a specific numeric GS1 AI primary identifier

`this.aiQualifiers = {"414":["254"],"8006":["22","10","21"],"8010":["8011"],"8017":["8019"],"8018":["8019"],"01":["22","10","21"]}`

### shortCodeToNumeric

returns an associative array that maps the alphabetic short names that can be used in the GS1 Digital Link to their numeric GS1 Application Identifier counterparts
is the inverse mapping of that provided by aiShortCode (see above)

`this.shortCodeToNumeric = {"lot":"10","ser":"21","cpv":"22","gdti":"253","glnx":"254","gcn":"255","ginc":"401","gsin":"402","gln":"414","payto":"415","grai":"8003","giai":"8004","itip":"8006","cpid":"8010","cpsn":"8011","gsrnp":"8017","gsrn":"8018","srin":"8019","sscc":"00","gtin":"01"}`

### twoDigitAIs

returns a list of two-digit GS1 Application Identifiers

### threeDigitAIs

returns a list of three-digit GS1 Application Identifiers

### fourDigitAIs

returns a list of four-digit GS1 Application Identifiers

### groupSeparator

groupSeparator returns ASCII character 29, 		`this.groupSeparator= String.fromCharCode(29);`


## Contributors  
- Mark Harrison mark.harrison@gs1.org

## Disclaimer  

This is still a pre-alpha release of the software, which still requires further testing.
It is provided on an as-is basis, with no warranty expressed or implied.
Neither GS1 nor the contributors accept any liability for its use nor for any damages caused through its use.

## Licence

Apache licence
# GS1 Digital Link linkset

This is a repository where we can play around with the format of the linkset returned from
any GS1 Digital Link resolver that makes use of the [linkset IETF Internet Draft](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-linkset-03).

# Linkset visualization 
The [linksetVisualization library](https://github.com/gs1/linkset/blob/master/gs1LinksetViz.js) renders a linkset as HTML. A set of [basic CSS rules](https://github.com/gs1/linkset/blob/master/gs1LinksetViz.css) is also provided as well as a [demo](https://gs1.github.io/linkset/)
# GS1DL-resolver-testsuite
This is the repository for the code behind the Resolver test suite, hosted at https://ref.gs1.org/test-suites/resolver/. It can be used to assess whether a resolver conforms to the GS1 Digital Link standard and is provided to encourage such conformance. The [resolver standard](https://ref.gs1.org/standards/resolver/) has several quirks that, sadly, can trip up the unwary.
 
The test suite is written as a JavaScript function that takes a GS1 Digital Link URI as input.  
 
 For each individual test, an object is created that includes:
 * the conformance criteria (copied from the standard);
 * the status of the test, which defaults to `fail`;
 * the 'fail' message to display;
 * a specific method that executes the test and sets the status to `pass` and updates the output message if appropriate.
Tests are either individual or closely related, such as when several tests are carried out from a single response to a query to the resolver. This means a lot of the code is executed asynchronously. This avoids all the fetch operations being triggered at once and creates the effect of the various tests appearing and, hopefully, switching from red to green as each one is executed. 
 
 The output is displayed in two ways:
 1. as a list of individual statements, styled to indicate `pass`, `fail` or `warn`;
 2. as a grid of coloured rectangles to give an immediate visual indication of the status of your resolver. Each square hyperlinks to the more detailed result.
 
The test suite creates both of these and inserts them into an HTML page as child elements of an element carrying an `id` of `gs1ResolverTests`. This is defined as a constant in the JavaScript file so that it can be changed if you wish.
 
As well as the [GS1 Digital Link Toolkit](https://github.com/gs1/GS1DigitalLinkToolkit.js), the script makes use of a set of functions in a [helper PHP file](https://github.com/gs1/GS1DL-resolver-testsuite/blob/master/tester.php). This is because it is easier to control HTTP requests using PHP and Curl than JavaScript's fetch. The PHP script returns an Object that contains the results of the HTTP HEAD request, which is then processed in the JavaScript.

Contributions welcome, noting the license under which the code is made available.

# Work in progress
There is still a significant amount of work to be done on the test suite and it's near-certain that there are bugs and other deficiencies that could lead to false results. Please raise an issue for any that you find or, even better, suggest code edits.

## 📢 Welcome to GS1 Resolver Community Edition Version 3.0.0

GS1 Resolver is a free and open-source web-server application that allows you to resolve GS1 identifiers to their corresponding web resources.

This is really useful for products, services, and other entities that have a GS1 identifier stored in a GS1 Digital Link QR Code.

In simple terms, a consumer scans the GS1 Digital Link QR Code on your product, and GS1 Resolver will redirect them to the correct page on your website,
all without having to change your existing web applications or databases. You simply add the GS1 identifier and the corresponding target URL to the Resolver database.

Even more useful is the fact that the same consumer could scan the QR Code before they purchase the product to check for nutritional red flags, and
after they have purchased the product to look at recipes! GS1 Resolver signposts people to the appropriate information based on <i>why</i> they scanned
the QR Code.

It means that that consumers, supply chain workers and others can see contextually important information about a product that is
relevant to their needs. One QR Code, infinite possibilities!

This software is developed by the GS1 Resolver Community and aims to be fully conformant with the GS1 Digital Link standard.

### <i>From the official 'GS1-Conformant Resolver Standard' document (link further down this README):

A GS1-Conformant Resolver connects a GS1-identified object or entity to one or more online
resources that are directly related to it. The object or entity may be identified at any level of
granularity, and the resources may be either human- or machine-readable. Examples include
product information pages, instruction manuals, patient leaflets and clinical data, product data,
service APIs, marketing experiences and more. By adhering to a common protocol based on existing
GS1 identifiers and existing Web technologies, each GS1-Conformant Resolver is part of a coherent,
yet distributed, network of links to information resources.</i>

### 🚀 What's new in this version?
1. **Completely revised and simplified architecture** for better performance and scalability.
2. **Improved support for GS1 Digital Link and GS1 Web URI** according to the standard published at https://ref.gs1.org/standards/resolver/
1. **Multiple Links**: Serve multiple links from a single context, a notable improvement over the previous single-link limitation. This is particularly useful if your product has multiple certificates or related documents.
2. **Simplified Data Input**: The data input methods have been revamped for user-friendliness. The complex structures of versions 1 and 2 are now obsolete, paving the way for straightforward data entry.
3. **Separate GTIN Qualifiers**: GTIN qualifiers are now independent, free from a fixed 'qualifier path', offering enhanced flexibility.
4. **Unified Database**: Streamline your infrastructure as maintaining both SQL *and* Document databases is no longer necessary—only the Document database is required.
5. **Embrace the Pythonic Way with Python 3.10**: The evolution of the Resolver CE is taking a leap forward in code readability with Python. After discussions and feedback from the dev community implementing Resolver 2.x, we've shed the many layers of Node JavaScript source files in favor of Python's elegant simplicity and fewer script files. Resolver CE v3.0 is written in Python 3.10, adopting a 'pythonic' style of coding that is much easier to read and adjust as required. This isn't just a change; it's an upgrade to high-performance processing that is easier to read, comprehend and adjust.
6. **Introduction of compression for GS1 Digital Link URls**: The Resolver CE v3.0 now supports the compression of GS1 Digital Link URLs. This feature is particularly useful when you have a long URL that you want to compress to a shorter one. The compressed URL can be used in place of the original URL, and the Resolver CE v3.0 will automatically decompress it when resolving the GS1 identifier.

### 📚 Simplified Architecture
The new architecture is based on a microservices approach. In this solution the data entry service with its API can be separated from the Front-end resolving web service.
The main components, each architected as separate container images, are:
1. **Data Entry Service**: This service is responsible for storing and managing the GS1 identifiers and their corresponding web resources.
2. **Front-end Web Service**: This service is responsible for resolving GS1 identifiers to their corresponding web resources, and redirecting web clients as needed
3. **Single Document Database** : This database is used to store the GS1 identifiers and their corresponding web resources in an IETF LinkSet format.
4. **Frontend Proxy Server**: This server is responsible for routing the incoming requests to the appropriate service when used together in a Docker composition or Kubernetes cluster.

<img alt="GS1 Resolver CE v3.0 Architecture.jpg" src="GS1%20Resolver%20CE%20v3.0%20Architecture.jpg" title="The simplified GS1 Resolver Community Edition version 3 architecture diagram"/>


Indeed, part of the innovative design is to make it possible to run Resolver CE v3.0 with just two containers:
1. Data Entry service running on your internal network
2. Resolving (web) service on the internet surface at id.<yourdomainname.com>

We can certainly foresee both these containers running as Azure Container Functions or similar inexpensive services on other cloud platforms.

**What about MongoDB?**
You could use a Mongo-cloud based solution such as MongoDB Atlas or Cosmos DB with Mongo APi connector. You then supply the connection string as an environment variable to data entry and web containers.

**What about the Proxy server?**
This container is just there to route incoming requests to data-entry and resolving (web) containers via a single endpoint through Docker or Kubernetes. Most of you have your own "front-door" routing services to your network applications, so you would just use that with appropriate rules.

<hr>

### What has been simplified compared to previous versions?

#### Two containers are dropped:
1. No relational database so the v1.x/v2.x SQL Server is dropped
2. No separate GS1 Digital Toolkit service - now integrated into data entry and web services
#### No more 'accounts'
1. Originally resolver v1/v2 of needed to be self-standing with independent logins. No more!
2. There is an authentication key that can be set as a secret and provided by the calling client when acting on the Resolver CE data entry API. Alternatively, you can easily replace our simple 'Bearer' authentication with your own authentication mechanism. You would likely run the data entry service on your internal network and accessed by your existing applications, with only the Resolving web server facing the internet - although they are both accessible via the provided proxy server 'out of the box'.

<hr>

### 📦 Installation
The GS1 Resolver Community Edition is available as a Docker composition. Make sure you have Docker Desktop running, then you can run the software using the following command from the root directory of the project:
```bash
docker compose up -d --build
```
This command will download the base container images from Docker Hub, build the necessary images, and start the services.
Importantly this will run whether you are using x64 (Intel / AMD) or ARM based hardware such as Apple Silicon and Raspberry Pi.

The service will then be available at http://localhost:8080

The API is available with Open API (Swagger) documentation at http://localhost:8080

### Postman documentation for the API can be found at: https://documenter.getpostman.com/view/10078469/2sA3JKeNb2

## What should I do next?
1. **Try it out**: To do this, use the 'setup_test.py' script in the tests folder to add some test data to the database and test Resolver. Indeed, we recommend you read through - then step through - the heavily documented test suite which will give you examples of creating / reading / deleting entries using the API, and observing behaviour through the Resolver front-end service.
2. **Put it to use**: You can now start using Resolver CE v3.0 in your projects. You'll be joining at least three GS1 Member Organisations who are already using Resolver CE v3.0 in various scenarios, and we are looking forward to hearing about your experiences.
3. **Review the new data entry format** in the /tests folder which gives examples of the new format for data entry - although you will be pleased to know that the API will accept v2.x format data as well.
3. **Look at the convertor scripts** in the useful_external_python_scripts folder. These scripts are useful for converting data between the previous versions of Resolver CE and the new format.
4. **Try out the API yourself**: The API is available with Open API (Swagger) documentation at http://localhost:8080 and, for Postman fans (complete with example data) at https://documenter.getpostman.com/view/10078469/2sA3JKeNb2
5. **Provide feedback**: We are looking for feedback from users to help us improve the software. Please provide feedback by creating an issue on the GitHub repository.

## Can I put this GS1 Resolver live?
YES! We recommend that you test the software thoroughly before putting it live. We are looking for feedback from users to help us improve the software. Please provide feedback by creating an issue on the GitHub repository.
Your code review to ensure security and GDPR compliance will also be a key consideration.
The only thing left is to decide on a Fully Qualified Domain Name (FQDN) for your Resolver service (we recommend a FQDN starting 'id' - e.g. 'https://id.mycompany.org' so it can sit alongside, but not disturb, your other web services) and set up the appropriate DNS records to point to your server.
Before you spin up the service, make sure you set environment variable 'FQDN' (currently in web_server/Dockerfile) to your chosen name.
You should also fill in your organisation contact information in web_server/src/public/gs1resolver.json which will be published as part
of the GS1 Resolver standard from https://your-fully-qualified-doman-name/.well-knowsn/gs1resolver

<hr>

## How do I backup the database?
The database is stored in a Docker volume within the composition. To back up the database to a backup archive file on your host computer, you can use the following command which uses 'docker compose exec' to run the 'mongodump' command within the 'database-service' container (some computers hosting docker may have 'docker-compose' rather than 'docker compose'):
```bash
 docker compose exec -T database-service mongodump --host localhost:27017 --username gs1resolver --password gs1resolver --archive=- --gzip > mongobackup.tar.gz
```
... and to restore the database from a backup archive file on your host computer, you can use the following command:
```bash
docker compose exec -T database-service mongorestore --host localhost:27017 --username gs1resolver --password gs1resolver --archive=- --gzip < mongobackup.tar.gz
```

## Looking for version Resolver CE v2.6?
We've stopped development and maintenance on version 2.6, but you can still find the code in the 'v2.6' branch of this repository:<br>
https://github.com/gs1/GS1_DigitalLink_Resolver_CE/tree/v2.6

We recommend that you upgrade to version 3.0 to take advantage of the new features, simplified services and many improvements.

## Settling in with Resolver CE v3.0?
It's now time to point your code branch back to the 'master' branch to keep up with the latest updates and improvements. We are looking forward to your feedback and contributions to the project.


## Resolver Test Suite
The Resolver Test Suite, where you can test that GS1 Resolvers are GS1 Digital Link Standard compliant, is on its way and will live here!

## Work in progress!
# EPCIS RDF Turtle Examples

We convert all JSON and JSON-LD examples to RDF Turtle automatically for two purposes:

- Turtle is easier to read than JSON-LD
- To validate the faithfulness of the JSON-LD representation and check the details of the corresponding RDF

## jsonld-cli

We use the `jsonld-cli` command-line tool, which uses the JSONLD Playground code and packages it as a `node.js` module (NPM).
- Source: https://github.com/digitalbazaar/jsonld-cli
- Package: https://www.npmjs.com/package/jsonld-cli
- Latest version: 0.3.0 (dated 2018)

### Installation

On Windows: install prerequisites (Python 2.7 and Microsoft CPP). Do this from `cmd`, not `cygwin bash`:
```
npm install --global --production windows-build-tools
setx VCTargetsPath "%programfiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V140"
```

Then install like this:
```
npm install -g jsonld-cli
```

You may get some warnings, they seem to be harmless. Eg:
```
npm WARN deprecated request@2.88.2: request has been deprecated, see https://github.com/request/request/issues/3142
npm WARN deprecated har-validator@5.1.5: this library is no longer supported
npm WARN deprecated request-promise-native@1.0.9: request-promise-native has been deprecated because it extends the now deprecated request package, see https://github.com/request/request/issues/3142
C:\Users\...\AppData\Roaming\npm\jsonld -> C:\Users\...\AppData\Roaming\npm\node_modules\jsonld-cli\bin\jsonld
+ jsonld-cli@0.3.0
added 3 packages from 11 contributors, removed 2 packages and updated 41 packages in 18.755s
```

### Help

The builtin help `jsonld -h` is quite poor, so we dug out the options from the source https://github.com/digitalbazaar/jsonld-cli/blob/master/bin/jsonld:
```
COMMON OPTIONS
  -i, --indent <spaces>                   spaces to indent [2]
  -N, --no-newline                        do not output the trailing newline [newline]
  -k, --insecure                          allow insecure SSL connections [false]
  -t, --type <type>                       input data type [auto]
  -b, --base <base>                       base IRI []
format [options] [filename|URL|-]     format and convert JSON-LD
  -f, --format <format>                   output format [json]
  -q, --nquads                            output application/nquads [false]
  -j, --json                              output application/json [true]
compact [options] [filename|URL]      compact JSON-LD
  -c, --context <filename|URL>            context filename or URL
  -S, --no-strict                         disable strict mode
  -A, --no-compact-arrays                 disable compacting arrays to single values
  -g, --graph                             always output top-level graph [false]
expand [options] [filename|URL|-]     expand JSON-LD
      --keep-free-floating-nodes          keep free-floating nodes
flatten [options] [filename|URL|-]    flatten JSON-LD
  -c, --context <filename|URL>            context filename or URL for compaction [none]
frame [options] [filename|URL|-]      frame JSON-LD
  -f, --frame <filename|URL>              frame to use
      --embed <embed>                     default @embed flag [true]
      --explicit <explicit>               default @explicit flag [false]
      --omit-default <omit-default>       default @omitDefault flag [false]
normalize [options] [filename|URL|-]  normalize JSON-LD
  -f, --format <format>                   format to output ('application/nquads' for N-Quads)
  -q, --nquads                            use 'application/nquads' format
```
The builtin help gives the following useful advice:
- The input parameter for all commands can be a filename, a URL beginning with "http://" or "https://", or "-" for stdin (the default).
- Input type can be specified as a standard content type or a simple string for common types. See the "request" extension code for available types. XML and HTML variations will be converted with an RDFa processor if available. If the input type is not specified it will be auto-detected based on file extension, URL content type, or by guessing with various parsers. Guessing may not always produce correct results.
- Output type can be specified for the "format" command and a N-Quads shortcut for the "normalize" command. For other commands you can pipe JSON-LD output to the "format" command.

## jena riot

`jsonld-cli` can output only `nquads`, eg:

```sh
jsonld format -f text/turtle ../JSON/Example_9.6.1-ObjectEvent.jsonld > Example_9.6.1-ObjectEvent.ttl
Error: ERROR: Unknown format: text/turtle
```

So we also use `riot` from Apache Jena:
- Download: https://jena.apache.org/download/

We make a file `prefixes.ttl` that defines the same prefixes as the EPCIS context, and postprocess with `riot` to make nicely formtted Turtle
(we use the fact that the `nquads` format output by `jsonld`, when no named graphs are used, is compatible with the `ttl` format):

```sh
jsonld format -q ../JSON/Example_9.6.1-ObjectEvent.jsonld | \
  cat prefixes.ttl - | riot -syntax ttl -formatted ttl > Example_9.6.1-ObjectEvent.ttl
```

## Context Issues

All JSON/JSON-LD examples declare their own context, usually something like this (first is the EPCIS context, then some custom extensions):

```json
  "@context": ["https://gs1.github.io/EPCIS/epcis-context.jsonld",
               {"example": "http://ns.example.com/epcis/"},
               {"gs1": "https://gs1.org/voc/"}],
```

The EPCIS context is served from a Github page and corresponds to the local version [../epcis-context.jsonld](../epcis-context.jsonld) in this repository
(it may show as a smaller file because it uses NL line endings, whereas the local version uses CR+NL line endings on Windows).
This means that:
- Whenever changes are made to [../epcis-context.jsonld](../epcis-context.jsonld), it will take time until it's deployed at Github pages. 
  Furthermore, Github pages aggressively use caching, so one may still get the old context.
- The version in development [../epcis-context-protected.jsonld](../epcis-context-protected.jsonld) cannot be tested so easily.

For example, error #201 still occurs for one of the examples because 
the change `xsd:decimal -> xsd:float` is still not deployed in the context.

TODO: see if option `-c` can override the context specified in-file.
# GS1 EPCIS 2.0 REST Bindings

This folder contains the work in progress for the EPCIS 2.0 REST interface. The [EPCIS 2.0 REST bindings](openapi.yaml) are described using OpenAPI 3.0 Specifications. A human friendly visualization of this file is provided via the [online Swagger Editor](https://editor.swagger.io/?url=https://raw.githubusercontent.com/gs1/EPCIS/master/REST%20Bindings/openapi.json).

Additionally two JSON schema files are available to describe the [EPCIS Query Language](query-schema.json) and the [EPCIS Query Schedule syntax](query-schedule.json).

The [openapi.yaml](openapi.yaml) file is the one that can be edited. Conversely, the [openapi.json](openapi.json) file is generated automatically (from `openapi.yaml`and the EPCIS JSON Schema) through the [Schema Injector tool](./schema-injector).

## Validating the OpenAPI specification for EPCIS 2.0

To ensure the validity of the [EPCIS REST bindings](openapi.yaml), use a validator such as openapi-spec-validator.
Assuming you have Python installed, install openapi-spec-validator:`pip install openapi-spec-validator`.
openapi-spec-validator can be executed from the terminal or loaded as a module. To run it from the terminal, type
`openapi-spec-validator openapi.yaml`.
# Schema Injector

This script allows injecting the EPCIS 2.0 JSON Schemas and examples (including XML examples) into the REST API Specification.
As a result there are no inconsistencies between the JSON Schemas and the REST API Spec. 

The script takes as input the `openapi.yaml` file and injects the corresponding subordinate files producing a final `openapi.json` file.

The `openapi.json` file is generated automatically and it shall never be edited manually. All changes must be made through the
`openapi.yaml` file. The `openapi.json` file is self-contained and can be published to any Open API 3.0.3 visualization tool.

To generate the final, single file, inlined spec you need to ensure you have installed 
the [Node.js](https://nodejs.org/en/download/) runtime and the [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) package manager.
You may also need to install sync-fetch using `npm install sync-fetch`.

Then on the command line just execute

```
npm install
chmod +x inject-schema.sh
inject-schema.sh
```

After successfully running the script above, the single, inlined specification `openapi.json` 
will be generated on the `REST Bindings` folder. It is included to allow 
Open API tools to just deal with one file. It contains all the Schemas and Open API constructs defined by the EPCIS 2.0 specification.
Events that involve `ErrorDeclaration` and `correctiveEventID`:

- `ErrorDeclarationAndCorrectiveEvent.jsonld`: transformation event (commissioning)
- `Example_9.6.1-ObjectEvent-with-error-declaration.jsonld`
  - TODO: this uses `urn:uuid:` which is not recommended for `eventID`, the `correctiveEvents` are not shown, and has a disconnected `receiving` event

Events that use DigitalLink URLs instead of EPC URNs

- `Example_9.6.1-ObjectEventWithDigitalLink.jsonld`: object event with `bizTransaction`
- `Example_9.6.2-ObjectEventWithDigitalLink.jsonld`: object event with transfer between `source` and `destination`
- `Example_9.6.3-AggregationEventWithDigitalLink.jsonld`: aggregation event
- `Example_9.6.4-TransformationEventWithDigitalLink.jsonld`: transformation event

Association events in JSON/JSON-LD  extracted from [AssociationEvents.xml](../../XML/AssociationEvent/AssociationEvents.xml):

- `AssociationEvent-a.jsonld`: `assembling`: association for physical objects such as assets and products:
   - reusable asset (GRAI, GIAI, SGTIN, CPID, ITIP, SSCC EPC URIs) to which one or more sensors are attached 
   - sensor which is mounted on/integrated into the asset 
- `AssociationEvent-b.jsonld`: `installing`: association for physical locations (identified via SGLN EPC URIs) equipped with ambient sensors
   - location (e.g. a cold storage room) to which one or more sensors are associated
- `AssociationEvent-c.jsonld`: `removing` (unpairing) sensor device from asset (`DELETE`), parallels case `a`
- `AssociationEvent-d.jsonld`: `disassembling`: like case `c`, but there are no child IDs at all, so we are disassembling all sub-objects
- `AssociationEvent-e.jsonld`: `assembling` with non-serialised IDs:
   - two childQuantities of particular product lots (LGTIN) are put into a returnable asset (GRAI)
- `AssociationEvent-f.jsonld`: has all fields of an ordinary event:
   - installing two individual assets (GIAI) and 4 products of a lot (LGTIN) in a returnable asset (GRAI)
   - also stating `bizTransaction` (a PO), transfer from a source `possessing_party` to a target `possessing_party`, and a sensor reading of `AbsoluteHumidity`
- `AssociationEvent-g.jsonld`: `disassembling` that is declared to be wrong with an ErrorDeclaration with `reason`: `incorrect_data` and has a `correctiveEventID`
- `AssociationEvent-h.jsonld`: `disassembling` expressed with correct parent (GRAI) and children (GIAIs) (correction of the event in the previous example)
# EPCIS JSON / JSON-LD Examples

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [EPCIS JSON / JSON-LD Examples](#epcis-json--json-ld-examples)
- [Validation of EPCIS event data in JSON / JSON-LD using JSON Schema and SHACL](#validation-of-epcis-event-data-in-json--json-ld-using-json-schema-and-shacl)
    - [EPCIS-JSON-Schema.json](#epcis-json-schemajson)
    - [EPCIS-SHACL.ttl](#epcis-shaclttl)
- [Conversion of EPCIS JSON / JSON-LD examples to RDF Linked Data](#conversion-of-epcis-json--json-ld-examples-to-rdf-linked-data)
- [Further information about JSON Schema](#further-information-about-json-schema)
- [Further information about W3C Shape Constraint Language (SHACL)](#further-information-about-w3c-shape-constraint-language-shacl)
- [General note about editing in this directory](#general-note-about-editing-in-this-directory)
- [List of Examples](#list-of-examples)

<!-- markdown-toc end -->

# Validation of EPCIS event data in JSON / JSON-LD using JSON Schema and SHACL

This directory has example files in JSON / JSON-LD  (JSON-LD with most of the  weirdness hidden in the @context header, which will eventually be remotely referenced from gs1.org)

Sibling directories also contain validation files:

## EPCIS-JSON-Schema.json

Initially developed by Danny Haak (Nedap), then modified by Mark Harrison,  Jose Montera Cantera Fonseca, Bhavesh Shah, Shalika Singh.

To try out JSON Schema validation of the examples, you can use online tools such as:

- https://www.jsonschemavalidator.net/
- https://jsonschemalint.com
- https://json-schema-validator.herokuapp.com/

Paste the contents of EPCIS-JSON-Schema.json into the 'Schema' window (which usually appears first or to the left)
Then paste the contents of one of the EPCIS example files into the 'Data' window (which usually appears second or to the right)
Any validation errors will be reported by the tools

## EPCIS-SHACL.ttl

Initially developed by Mark Harrison, then modified by Vladimir Alexiev and Martin Kotov.

To try out Shape Constraint Language (SHACL) validation, you can use this online validation tool:

- https://shacl.org/playground/

Paste the contents of EPCIS-SHACL.ttl into the 'Shapes Graph' window on the left-hand side
Paste the contents of one of the EPCIS example files into the 'Data Graph' window on the right-hand side.
Press both 'Update' buttons under the two  main text areas where you have just pasted in contents of files.

If there are validation errors, they will appear in the Validation Report window (bottom-right).
If there are no validation errors, the Validation Report window should be empty.

# Conversion of EPCIS JSON / JSON-LD examples to RDF Linked Data

The contents of any of the EPCIS example files can also be pasted into this online tool:

https://json-ld.org/playground/

This JSON-LD playground tool:

- Performs a basic check that the data is valid JSON-LD - although it has no awareness of our EPCIS-SHACL.ttl file.
- Converts between different JSON-LD renditions, eg Normalised, Compacted, Expanded
- Performs conversion of JSON-LD data into other RDF (Linked Data formats),
  such as N-Quads (consisting of Subject-Predicate-Object-Graph quads)
- Now also includes a tabular view, as well as a visualisation as  a branching diagram.

# Further information about JSON Schema

JSON Schema may be familiar to many Web / app developers, particularly since the Open API specification makes use of it.

Further information about JSON Schema can be found at: https://json-schema.org/

# Further information about W3C Shape Constraint Language (SHACL)

Shape Constraint Language (SHACL) may be less familiar, even though it is a relatively new W3C technical recommendation (standard)

The W3C SHACL standard is available at: https://www.w3.org/TR/shacl/

# General note about editing in this directory

If you notice any validation errors in the examples, please contact mark.harrison@gs1.org so that we can investigate further.

Please only edit the existing JSON Schema file or SHACL file if you know what you are doing!

Please only edit the existing JSON / JSON-LD EPCIS examples if you know what you are doing 
- but feel free to take a copy or contribute additional example files.

# List of Examples

Examples were derived from XML examples, then significantly added and commented by Vladmir Alexiev, Greg Rowe, Craig Alan Repec and other WG members

- `Example-TransactionEvents-2020_07_03y.jsonld`: custom transactions (summarising discharge from a hospital, passage of rail cars)
- `Example-Type-sourceOrDestination,measurement,bizTransaction.jsonld`: shows the disambiguation of JSON field `type` to different RDF properties:
  - `epcis:bizTransactionType` (from `epcis:BizTransaction` to `cbv:BTT`)
  - `epcis:measurementType` (from `epcis:SensorReport` to `gs1:MeasurementType`)
  - `epcis:sourceOrDestinationType` (from `epcis:SourceOrDestination` to `cbv:SDT`)
- `Example_9.6.1-ObjectEvent.jsonld`: object event involving businessTransactions
- `Example_9.6.1-with-comment.jsonld`: object event with custom field and a comment
- `Example_9.6.2-ObjectEvent.jsonld`: object event involving source and destination
- `Example_9.6.3-AggregationEvent.jsonld`: aggregation events involving childEPCs and childQuantityLists
- `Example_9.6.4-TransformationEvent.jsonld`: transformation event with `ilmd` (Instance/Lot Master Data)
- `PersistentDisposition-example.jsonld`: aggregation event involving the change of persistent disposition from `completeness_inferred` to `completeness_verified`

Further explanations about individual examples are found in sub-directories
# EPCIS event data with sensorElementList in JSON / JSON-LD format

This directory has example files in JSON / JSON-LD. 
Most of them are derived from the XML examples in [SensorDataExamples.xml](../../XSD/SensorDataExamples.xml), but we have added some more:

- `SensorDataExample1.jsonld`: 3 sensor readings of several properties (`Temperature, Absolute Humidity, Speed, Illuminance`) 
  of a particular SGTIN at different `time` instants (here: 30 minutes apart). 
  Sensor `deviceID` is a GIAI. Includes `deviceMetadata` and `rawData` URLs
- `SensorDataExample1b.jsonld`: 3 sensor readings, but no GTIN is mentioned, so the readings apply to the `readPoint` itself
  - Also includes explicit `type` specifying `SensorElement` (not needed)
- `SensorDataExample2.jsonld`:  Based on the same data as 1, but reports `min/max/meanValue` over a time interval (a more compact form)
- `SensorDataExample3.jsonld`:  An interval reading, but no GTIN is mentioned (note that there is no object ID in the What dimension), 
  so the reading applies to the `readPoint` itself, i.e. documents the storage conditions of that location 
- `SensorDataExample4.jsonld`:  1 sensor reading of a particular quantity of a LGTIN, using 4 different sensors. 
   - Includes `deviceMetadata` and `rawData` URLs for each sensor (`rawData` vary with `sensorID` and `time`)
- `SensorDataExample5.jsonld`:  Transmits time-stamped sensor data (to be discouraged unless there is a strong reason to do so)
- `SensorDataExample6.jsonld`:  An interval reading with comprehensive statistical measures (`minValue, maxValue, meanValue, sDev, percRank, percValue`) over interval `startTime, endTime`.
   Also includes a custom MeasurementType `someSensorProperty` that uses `stringValue`, and custom `furtherSensorData` with extra custom props (user/vendor extensions)
- `SensorDataExample7.jsonld`:  Custom MeasurementTypes using non-numeric values (`stringValue, booleanValue, uriValue, hexBinaryValue`)
- `SensorDataExample8.jsonld`:  An interval report of Absolute Humidity and Temperature
   - And the concentration of:
     - A `chemicalSubstance` (using an INCHI key URL)
     - A `microorganism` (using a NCBI taxonomy URL)
  - It seems the goods have become moldy!
- `SensorDataExample9.jsonld`:  SensorElement with `ERROR_CONDITION` (further described with a URI) and an `ALARM_CONDITION` (described with boolean `true`)
- `SensorDataExample10.jsonld`: Reports the speed vector of a SGTIN using 3 `components` (`x, y, z`).
   - Also uses the custom prop `ex:feature` to state the speed Reading applies to the product itself.
- `SensorDataExample11.jsonld`: Transaction with step `inspecting` and disposition `needs_replacement` with sensor data showing `EffectiveDoseRate` measured in `P71` (millisievert per hour) of two GTINs.
  It Seems the goods have absorbed too much radiation!
- `SensorDataExample12.jsonld`: Transformation with sensorReport and user extensions in all areas where they are allowed (`procedure, machine, furtherSensorData` etc)
- `SensorDataExample13.jsonld`: Uses the custom property `ex:feature` to report the outside `Temperature` (`ex:ambiance`) vs the `Temperature` of the product package (`ex:outerPackage`).
  - Uses bizStep `sensor_reporting`, which is a new addition to CBV 2.0; the other examples use `inspecting`, which is less specific.
  - USes Web URIs (GS1 DL URIs) rather than EPC URNs
- `SensorDataExample14.jsonld`: Event conveying geographic coordinates as `Latitude, Longitude` (being `Angle` in `DD`) using the default Coordinate Reference System (WGS84), which does not need to be indicated
- `SensorDataExample15.jsonld`: Event conveying the same coordinates as `Easting, Northing` (being `Length` in `MTR`) using a Coordinate Reference System (CRS) other than WGS84
  - Namely, this uses https://epsg.io/27700 OSGB 1936 / British National Grid (Ordnance Survey of Great Britain).
  - You can see the conversion at https://epsg.io/transform#s_srs=4326&t_srs=27700&x=23.3199410&y=42.6983340,
  - You can browse for the OGC EPSG URL to use at http://www.opengis.net/def/crs/EPSG/0/ (where /0/ indicates the "latest version" or version-independent URL of that CRS)
- `SensorDataExample16.jsonld`: Event conveying the same coordinates using the [geo: URI scheme](https://en.wikipedia.org/wiki/Geo_URI_scheme) ([RFC5870](https://datatracker.ietf.org/doc/html/rfc5870)), which is a much shorter way. 
  - However, `geo:` URIs can use only two fixed CRS (see [RFC5870 section 8.3](https://datatracker.ietf.org/doc/html/rfc5870#section-8.3) and [IANA geo-uri-parameters](https://iana.org/assignments/geo-uri-parameters/geo-uri-parameters.xhtml):
    - `EPSG::4326`, which is WGS84 (2D)
    - `EPSG::4979`, which is WGS84 with altitude (3D)
  - Whereas the "long-hand" approach with `component` and `coordinateReferenceSystem` can use any EPSG or OGC coordinate system
- `SensorDataExample17.jsonld`: Uses the custom property `ex:feature` to report 3 `Mass` readings of a SGTIN:
   tare (`ex:packaging`), net (`ex:product`), gross (`ex:total`)
Includes RDF diagrams made from the [Turtle](../Turtle) examples using [rdfpuml](https://github.com/VladimirAlexiev/rdf2rml).

TODO:
- Automate with Makefile. See the Turtle makefile for using `make` macros, and ask me for a typical body of commands
- `puml.ttl` are `puml:` instructions that MAY be applicable to all examples.
- Enable per-file `puml:` instructions, eg `Example-Type-sourceOrDestination,measurement,bizTransaction.puml.ttl` to be used together with `Example-Type-sourceOrDestination,measurement,bizTransaction.ttl`

These commands process one file, but they do it in a very wrong way...
```
cp -f ../Turtle/prefixes.ttl .
cat ../Turtle/Example-Type-sourceOrDestination,measurement,bizTransaction.ttl puml.ttl Example-Type-sourceOrDestination,measurement,bizTransaction.puml.ttl > temp.ttl
rdfpuml.bat temp.ttl
puml.bat temp.puml
mv temp.png Example-Type-sourceOrDestination,measurement,bizTransaction.png
rm temp.ttl temp.puml
```
# EPCIS and CBV 2.0 Ontologies and Shape

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [EPCIS and CBV 2.0 Ontologies and Shape](#epcis-and-cbv-20-ontologies-and-shape)
    - [Ontologies](#ontologies)
    - [Ontology Checks](#ontology-checks)
    - [Property Checks](#property-checks)
    - [Conversion to JSONLD](#conversion-to-jsonld)
        - [Jena riot](#jena-riot)
        - [ttl2json](#ttl2json)
        - [jsonld-cli](#jsonld-cli)
        - [jq](#jq)
    - [RDF Shape](#rdf-shape)

<!-- markdown-toc end -->

## Ontologies

These are draft and subject to change

- Downloaded from https://ns.mh1.eu/epcis/ and https://ns.mh1.eu/cbv/ (View Source and then save the JSON-LD fragments)
- Converted to Turtle using the same process described in [../Turtle](../Turtle), then sorting in a better way
  - WARNING: `make` overwrites the Turtle files from JSONLD files. 
    If in the future we decide to use Turtle as the master source, this needs to change.
- Adopted Turtle as master ontology format
  - Keep it organized in sections (Classes, Properties) and sorted by "paragraph" in each section
- Made ontology improvements:
  - #230 `Source` vs `Destination` class merged to `SourceOrDestination`
  - #260 disambiguate `type` to `bizTransactionType, measurementType, sourceOrDestinationType`
  - etc, etc
- Generate good JSONLD from it (see below), to be used in the web documentation browser

## Ontology Checks

#258
`ontology-check.sh` uses the "paragraph" structure of the 2 ontology Turtle files to do some basic checks and ensure that all ontology terms:

- have a label,
- have a definition,
- have isDefinedBy, 
- have `sw:term_status "stable"`
- don't have `TODO`

## Property Checks

`ontology-props.rq` makes a table of all `epcis:` props with their domains and ranges

- load EPCIS.ttl to a RDF respository
- run this query and capture the table (eg as tsv)
- check against the [google sheet of properties](https://docs.google.com/spreadsheets/d/19lseUd1kHiz48VNtrHXy6kafLTlNzS1GsaYiBqdT4UA/edit#gid=606879607)

`ontology-prop-checks.rq` checks for props with:

- mismatching `rdfs:domain` and `schema:domainIncludes`
- mismatching `rdfs:range` and `schema:rangeIncludes`
- `rdf:Property` but not `owl:ObjectProperty` or `owl:DatatypeProperty` and vice versa
- `owl:DatatypeProperty` but range is not a `xsd:` datatype
- `owl:ObjectProperty` with range not in `epcis:, cbv:` or `gs1:`
- `owl:DatatypeProperty` with range `xsd:anyURI` should be changed to `owl:ObjectProperty`, see #206

## Conversion to JSONLD

#238
We use some complementary tools to convert Turtle to the best possible JSON-LD:
- `CBV.ttl` to `CBV.jsonld`
- `EPCIS.ttl` to `EPCIS.jsonld`

### Jena riot

Download and install from Jena; `riot` comes as part of it

- cons: emits lists as `rdf:List` long-hand using blank nodes and `first/rest`
- cons: can't specify a custom context
- pro: generates a richer context by examining the values of each property, eg:

```json
{"@context":
  {"domainIncludes" : {"@id" : "http://schema.org/domainIncludes", "@type" : "@id"}}
}
```

This allows compact representation of properties, eg
```json
"@graph": [
  {"@id" : "epcis:action", 
   "domainIncludes" : [ "epcis:AssociationEvent", "epcis:ObjectEvent", "epcis:AggregationEvent", "epcis:TransactionEvent" ]}]}
```

I've extracted and saved this context to `EPCIS-CBV-context.jsonld`,
then added fixed `@language` to `comment` because all our definitions are in English:
```json
    "comment": {
      "@id": "http://www.w3.org/2000/01/rdf-schema#comment",
      "@language": "en"
    },
```

### ttl2json

```
npm install -g @frogcat/ttl2jsonld
```

- Pro: emits lists in short-hand, eg

```json
  {"@id":"epcis:epcClass",
   "rdfs:domain":{
    "@type":"owl:Class",
    "owl:unionOf":{"@list":[{"@id":"gs1:Product"}, {"@id":"gs1:ProductBatch"}]}}}
```

- cons: generates a simple context only using the Turtle prefixes
- cons: can't specify a custom context

### jsonld-cli

```
npm install -g jsonld-cli
```
(See [../Turtle/README.md](../Turtle/README.md) for more details.)

- Cons: can't specify input file type, thus can't convert RDF->JSONLD, see https://github.com/digitalbazaar/jsonld-cli/issues/19
- Pro: can compact JSON-LD properties while preserving compact lists
- Pro: can specify custom context
  - Cons: the context must be a file (or URL), cannot be inline
  - Uses this specific syntax for the filename, eg `jsonld compact -c file://EPCIS-CBV-context.jsonld`
  - The context cannot be embedded in the output as I want it to be (so the JSONLD is self-contained)
  - Emits the same filename as remote context in the output, which causes an error in another tool:

```
riot -syntax jsonld -formatted ttl EPCIS.jsonld
ERROR riot :: loading remote context failed: file://EPCIS-CBV-context.jsonld
```

### jq

To overcome the cons of `jsonld` described above, we need to do some advanced JSON surgery.

`jq` is the tool for that, install from https://stedolan.github.io/jq/download/ .

Then the overall pipeline to do the conversion looks like this (see `Makefile`):

```
ttl2jsonld EPCIS.ttl \
 | jsonld compact -c file://EPCIS-CBV-context.jsonld \
 | jq -S --slurpfile c EPCIS-CBV-context.jsonld '.["@context"] |= $c[0]["@context"]' \
 > EPCIS.jsonld
```

```
ttl2jsonld CBV.ttl \
 | jsonld compact -c file://EPCIS-CBV-context.jsonld \
 | jq -S --slurpfile c EPCIS-CBV-context.jsonld '.["@context"] |= $c[0]["@context"]' \
 > CBV.jsonld
```


- The `jq` step slurps the context file to variable `$c`, then
  replaces the field `"@context"` (being `"file://EPCIS-CBV-context.jsonld"`)
  with its content (stripping a top-level array and dict).
- For good measure, we also use `-S` to sort the fields (keys) of each ontology term (JSONLD object) alphabetically

Then we can validate that the JSONLD is correct by converting back to formatted Turtle:

```
riot --formatted ttl EPCIS.jsonld | less
```

(but the order of ontology terms is not preserved)

## RDF Shape

[EPCIS-SHACL.ttl](EPCIS-SHACL.ttl) is a draft SHACL shape for describing EPCIS events, initially developed by Mark Harrison then improved by Vladimir Alexiev and Martin Kotov.

To try out Shape Constraint Language (SHACL) validation, you can use this online validation tool:

https://shacl-playground.zazuko.com/

- Paste the contents of EPCIS-SHACL.ttl into the 'Shapes Graph' window on the left-hand side
- Paste the contents of one of the EPCIS example files into the 'Data Graph' window on the right-hand side.
- If there are validation errors, they will appear in the Validation Report panel.
- If there are no validation errors, the Validation Report window should say 'Success'.
- For details about errors, click on the 'bug' icon top-left, then select 'Display errors as Raw RDF'.

Note that https://shacl.org/playground/ appears not to fully support JSON-LD v1.1 features used in our JSON-LD context file for EPCIS/CBV, so it is no longer recommended for testing SHACL validation for EPCIS/CBV.

Further information about W3C Shape Constraint Language (SHACL)

- SHACL may be less familiar as it is a relatively new W3C technical recommendation (standard)
- The W3C SHACL standard is available at: https://www.w3.org/TR/shacl/
- These are examples from https://www.mimasu.nl/epcis/xmljson
- This is also an EPCIS XML to JSON convertor
- There are also a couple of examples from https://developers.evrythng.com/docs/epcis-20-repository
# EPCIS
Draft files being shared for EPCIS 2.0 development. The repository is organised by work streams, one folder for each work stream (e.g., JSON/JSON-LD, REST bindings, etc.)

The draft EPCIS 2.0 and CBV 2.0 specifications and corresponding artefacts were in PUBLIC REVIEW until 11th November 2021 at:
https://www.gs1.org/standards/development-work-groups/public-reviews#EPCISCBV_Public-Review-2021
Commenting has now closed.  Many thanks to everyone who has provided feedback.
The editorial team has already begun reviewing every comment received and will be making improvements accordingly.

Please use this link to download the .zip (including the public review drafts of the EPCIS / CBV 2.0 standards).
Please do not attempt to submit any public review comments as GitHub issues - we needed them to be submitted via the official GS1 mechanism so that they can be formally considered by the work group.  

Anyone was able to submit comments, whether you participate in the GS1 Global Standards Management Process (GSMP) or not - further details were at the link above.

Public review for EPCIS/CBV 2.0 ended on 11th November 2021.  Many thanks for all the feedback.

The current ratified standards are available at https://ref.gs1.org/standards/epcis and https://ref.gs1.org/standards/cbv

Normative artefacts are available at https://ref.gs1.org/standards/epcis/artefacts

Example data are available at https://ref.gs1.org/docs/epcis/examples

Ontologies for EPCIS and CBV are available at https://ref.gs1.org/epcis and https://ref.gs1.org/cbv
Events that involve `ErrorDeclaration` and `correctiveEventID`:

- `ErrorDeclarationAndCorrectiveEvent.jsonld`: transformation event (commissioning)
- `Example_9.6.1-ObjectEvent-with-error-declaration.jsonld`
  - TODO: this uses `urn:uuid:` which is not recommended for `eventID`, the `correctiveEvents` are not shown, and has a disconnected `receiving` event

Events that use DigitalLink URLs instead of EPC URNs

- `Example_9.6.1-ObjectEventWithDigitalLink.jsonld`: object event with `bizTransaction`
- `Example_9.6.2-ObjectEventWithDigitalLink.jsonld`: object event with transfer between `source` and `destination`
- `Example_9.6.3-AggregationEventWithDigitalLink.jsonld`: aggregation event
- `Example_9.6.4-TransformationEventWithDigitalLink.jsonld`: transformation event

Association events in JSON/JSON-LD  extracted from [AssociationEvents.xml](../../XML/AssociationEvent/AssociationEvents.xml):

- `AssociationEvent-a.jsonld`: `assembling`: association for physical objects such as assets and products:
   - reusable asset (GRAI, GIAI, SGTIN, CPID, ITIP, SSCC EPC URIs) to which one or more sensors are attached 
   - sensor which is mounted on/integrated into the asset 
- `AssociationEvent-b.jsonld`: `installing`: association for physical locations (identified via SGLN EPC URIs) equipped with ambient sensors
   - location (e.g. a cold storage room) to which one or more sensors are associated
- `AssociationEvent-c.jsonld`: `removing` (unpairing) sensor device from asset (`DELETE`), parallels case `a`
- `AssociationEvent-d.jsonld`: `disassembling`: like case `c`, but there are no child IDs at all, so we are disassembling all sub-objects
- `AssociationEvent-e.jsonld`: `assembling` with non-serialised IDs:
   - two childQuantities of particular product lots (LGTIN) are put into a returnable asset (GRAI)
- `AssociationEvent-f.jsonld`: has all fields of an ordinary event:
   - installing two individual assets (GIAI) and 4 products of a lot (LGTIN) in a returnable asset (GRAI)
   - also stating `bizTransaction` (a PO), transfer from a source `possessing_party` to a target `possessing_party`, and a sesnor reading of `Humidity`
- `AssociationEvent-g.jsonld`: `disassembling` that is declared to be wrong with an ErrorDeclaration with `reason`: `incorrect_data` and has a `correctiveEventID`
- `AssociationEvent-h.jsonld`: `disassembling` expressed with correct parent (GRAI) and children (GIAIs) (correction of the event in the previous example)
# EPCIS JSON / JSON-LD Examples

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [EPCIS JSON / JSON-LD Examples](#epcis-json--json-ld-examples)
- [Validation of EPCIS event data in JSON / JSON-LD using JSON Schema and SHACL](#validation-of-epcis-event-data-in-json--json-ld-using-json-schema-and-shacl)
    - [EPCIS-JSON-Schema.json](#epcis-json-schemajson)
    - [EPCIS-SHACL.ttl](#epcis-shaclttl)
- [Conversion of EPCIS JSON / JSON-LD examples to RDF Linked Data](#conversion-of-epcis-json--json-ld-examples-to-rdf-linked-data)
- [Further information about JSON Schema](#further-information-about-json-schema)
- [Further information about W3C Shape Constraint Language (SHACL)](#further-information-about-w3c-shape-constraint-language-shacl)
- [General note about editing in this directory](#general-note-about-editing-in-this-directory)
- [List of Examples](#list-of-examples)

<!-- markdown-toc end -->

# Validation of EPCIS event data in JSON / JSON-LD using JSON Schema and SHACL

This directory has example files in JSON / JSON-LD  (JSON-LD with most of the  weirdness hidden in the @context header, which will eventually be remotely referenced from gs1.org)

Sibling directories also contain validation files:

## EPCIS-JSON-Schema.json

Initially developed by Danny Haak (Nedap), then modified by Mark Harrison,  Jose Montera Cantera Fonseca, Bhavesh Shah, Shalika Singh.

To try out JSON Schema validation of the examples, you can use online tools such as:

- https://www.jsonschemavalidator.net/
- https://jsonschemalint.com
- https://json-schema-validator.herokuapp.com/

Paste the contents of EPCIS-JSON-Schema.json into the 'Schema' window (which usually appears first or to the left)
Then paste the contents of one of the EPCIS example files into the 'Data' window (which usually appears second or to the right)
Any validation errors will be reported by the tools

## EPCIS-SHACL.ttl

Initially developed by Mark Harrison, then modified by Vladimir Alexiev and Martin Kotov.

To try out Shape Constraint Language (SHACL) validation, you can use this online validation tool:

- https://shacl.org/playground/

Paste the contents of EPCIS-SHACL.ttl into the 'Shapes Graph' window on the left-hand side
Paste the contents of one of the EPCIS example files into the 'Data Graph' window on the right-hand side.
Press both 'Update' buttons under the two  main text areas where you have just pasted in contents of files.

If there are validation errors, they will appear in the Validation Report window (bottom-right).
If there are no validation errors, the Validation Report window should be empty.

# Conversion of EPCIS JSON / JSON-LD examples to RDF Linked Data

The contents of any of the EPCIS example files can also be pasted into this online tool:

https://json-ld.org/playground/

This JSON-LD playground tool:

- Performs a basic check that the data is valid JSON-LD - although it has no awareness of our EPCIS-SHACL.ttl file.
- Converts between different JSON-LD renditions, eg Normalised, Compacted, Expanded
- Performs conversion of JSON-LD data into other RDF (Linked Data formats),
  such as N-Quads (consisting of Subject-Predicate-Object-Graph quads)
- Now also includes a tabular view, as well as a visualisation as  a branching diagram.

# Further information about JSON Schema

JSON Schema may be familiar to many Web / app developers, particularly since the Open API specification makes use of it.

Further information about JSON Schema can be found at: https://json-schema.org/

# Further information about W3C Shape Constraint Language (SHACL)

Shape Constraint Language (SHACL) may be less familiar, even though it is a relatively new W3C technical recommendation (standard)

The W3C SHACL standard is available at: https://www.w3.org/TR/shacl/

# General note about editing in this directory

If you notice any validation errors in the examples, please contact mark.harrison@gs1.org so that we can investigate further.

Please only edit the existing JSON Schema file or SHACL file if you know what you are doing!

Please only edit the existing JSON / JSON-LD EPCIS examples if you know what you are doing 
- but feel free to take a copy or contribute additional example files.

# List of Examples

Examples were derived from XML examples, then significantly added and commented by Vladmir Alexiev, Greg Rowe, Craig Alan Repec and other WG members

- `Example-TransactionEvents-2020_07_03y.jsonld`: custom transactions (summarising discharge from a hospital, passage of rail cars)
- `Example-Type-sourceOrDestination,measurement,bizTransaction.jsonld`: shows the disambiguation of JSON field `type` to different RDF properties:
  - `epcis:bizTransactionType` (from `epcis:BizTransaction` to `cbv:BTT`)
  - `epcis:measurementType` (from `epcis:SensorReport` to `gs1:MeasurementType`)
  - `epcis:sourceOrDestinationType` (from `epcis:SourceOrDestination` to `cbv:SDT`)
- `Example_9.6.1-ObjectEvent.jsonld`: object event involving businessTransactions
- `Example_9.6.1-with-comment.jsonld`: object event with custom field and a comment
- `Example_9.6.2-ObjectEvent.jsonld`: object event involving source and destination
- `Example_9.6.3-AggregationEvent.jsonld`: aggregation events involving childEPCs and childQuantityLists
- `Example_9.6.4-TransformationEvent.jsonld`: transformation event with `ilmd` (Instance/Lot Master Data)
- `PersistentDisposition-example.jsonld`: object event involving the change of persistent disposition from `completeness_inferred` to `completeness_verified`

Further explanations about individual examples are found in sub-directories
# EPCIS event data with sensorElementList in JSON / JSON-LD format

This directory has example files in JSON / JSON-LD. 
Most of them are derived from the XML examples in [SensorDataExamples.xml](../../XSD/SensorDataExamples.xml), but we have added some more:

- `SensorDataExample1.jsonld`: 3 sensor readings of several properties (`Temperature, Absolute Humidity, Speed, Illuminance`) 
  of a particular SGTIN at different `time` instants (here: 30 minutes apart). 
  Sensor `deviceID` is a GIAI. Includes `deviceMetadata` and `rawData` URLs
- `SensorDataExample1b.jsonld`: 3 sensor readings, but no GTIN is mentioned, so the readings apply to the `readPoint` itself
  - Also includes explicit `type` specifying `SensorElement` (not needed)
- `SensorDataExample2.jsonld`:  Based on the same data as 1, but reports `min/max/meanValue` over a time interval (a more compact form)
- `SensorDataExample3.jsonld`:  An interval reading, but no GTIN is mentioned (note that there is no object ID in the What dimension), 
  so the reading applies to the `readPoint` itself, i.e. documents the storage conditions of that location 
- `SensorDataExample4.jsonld`:  1 sensor reading of a particular quantity of a LGTIN, using 4 different sensors. 
   - Includes `deviceMetadata` and `rawData` URLs for each sensor (`rawData` vary with `sensorID` and `time`)
- `SensorDataExample5.jsonld`:  Transmits time-stamped sensor data (to be discouraged unless there is a strong reason to do so)
- `SensorDataExample6.jsonld`:  An interval reading with comprehensive statistical measures (`minValue, maxValue, meanValue, sDev, percRank, percValue`) over interval `startTime, endTime`.
   Also includes a custom MeasurementType `someSensorProperty` that uses `stringValue`, and custom `furtherSensorData` with extra custom props (user/vendor extensions)
- `SensorDataExample7.jsonld`:  Custom MeasurementTypes using non-numeric values (`stringValue, booleanValue, uriValue, hexBinaryValue`)
- `SensorDataExample8.jsonld`:  An interval report of Absolute Humidity and Temperature
   - And the concentration of:
     - A `chemicalSubstance` (using an INCHI key URL)
     - A `microorganism` (using a NCBI taxonomy URL)
  - It seems the goods have become moldy!
- `SensorDataExample9.jsonld`:  SensorElement with `ERROR_CONDITION` (further described with a URI) and an `ALARM_CONDITION` (described with boolean `true`)
- `SensorDataExample10.jsonld`: Reports the speed vector of a SGTIN using 3 `components` (`x, y, z`).
   - Also uses the custom prop `ex:feature` to state the speed Reading applies to the product itself.
- `SensorDataExample11.jsonld`: Transaction with step `inspecting` and disposition `needs_replacement` with sensor data showing `EffectiveDoseRate` measured in `P71` (millisievert per hour) of two GTINs.
  It Seems the goods have absorbed too much radiation!
- `SensorDataExample12.jsonld`: Transformation with sensorReport and user extensions in all areas where they are allowed (`procedure, machine, furtherSensorData` etc)
- `SensorDataExample13.jsonld`: Uses the custom property `ex:feature` to report the outside `Temperature` (`ex:ambiance`) vs the `Temperature` of the product package (`ex:outerPackage`).
  - Uses bizStep `sensor_reporting`, which is a new addition to CBV 2.0; the other examples use `inspecting`, which is less specific.
  - USes Web URIs (GS1 DL URIs) rather than EPC URNs
- `SensorDataExample14.jsonld`: Event conveying geographic coordinates as `latitude, longitude` (being `Angle` in `DD`) using the default Coordinate Reference System (WGS84), which does not need to be indicated
- `SensorDataExample15.jsonld`: Event conveying the same coordinates as `easting, northing` (being `Length` in `MTR`) using a Coordinate Reference System (CRS) other than WGS84
  - Namely, this uses https://epsg.io/27700 OSGB 1936 / British National Grid (Ordnance Survey of Great Britain).
  - You can see the conversion at https://epsg.io/transform#s_srs=4326&t_srs=27700&x=23.3199410&y=42.6983340,
  - You can browse for the OGC EPSG URL to use at http://www.opengis.net/def/crs/EPSG/0/ (where /0/ indicates the "latest version" or version-independent URL of that CRS)
- `SensorDataExample16.jsonld`: Event conveying the same coordinates using the [geo: URI scheme](https://en.wikipedia.org/wiki/Geo_URI_scheme) ([RFC5870](https://datatracker.ietf.org/doc/html/rfc5870)), which is a much shorter way. 
  - However, `geo:` URIs can use only two fixed CRS (see [RFC5870 section 8.3](https://datatracker.ietf.org/doc/html/rfc5870#section-8.3) and [IANA geo-uri-parameters](https://iana.org/assignments/geo-uri-parameters/geo-uri-parameters.xhtml):
    - `EPSG::4326`, which is WGS84 (2D)
    - `EPSG::4979`, which is WGS84 with altitude (3D)
  - Whereas the "long-hand" approach with `component` and `coordinateReferenceSystem` can use any EPSG or OGC coordinate system
- `SensorDataExample17.jsonld`: Uses the custom property `ex:feature` to report 3 `Mass` readings of a SGTIN:
   tare (`ex:packaging`), net (`ex:product`), gross (`ex:total`)
# EPCIS RDF Turtle Examples

## Converting JSON-LD with Playground

The contents of the EPCIS JSON example files can be pasted into this online tool:

https://json-ld.org/playground/

- This JSON-LD playground tool performs a basic check that the data is valid JSON-LD - although it has no awareness of our EPCIS-SHACL.ttl file.
- The JSON-LD playground tool also performs conversion of JSON-LD data into other Linked Data formats such as N-Quads (consisting of Subject-Predicate-Object or Subject-Property-Value triples).
- The JSON-LD playground tool now also includes a tabular view, as well as a visualisation as  a branching diagram.

## jsonld-cli

We convert all JSON and JSON-LD examples to RDF Turtle automatically for two purposes:

- Turtle is easier to read than JSON-LD
- To validate the faithfulness of the JSON-LD representation and check the details of the corresponding RDF

We use the `jsonld-cli` command-line tool, which uses the JSONLD Playground code and packages it as a `node.js` module (NPM).
- Source: https://github.com/digitalbazaar/jsonld-cli
- Package: https://www.npmjs.com/package/jsonld-cli
- Latest version: 0.3.0 (dated 2018). PLEASE USE THIS ONE

Even this latest version of `jsonld-cli` doesn't implement all features of the jsonld playground,
see issue [jsonld-cli#18](https://github.com/digitalbazaar/jsonld-cli/issues/18).
But we were able to work around these issues in the JSONLD context.

### Installation

On Windows: install prerequisites (Python 2.7 and Microsoft CPP). Do this from `cmd`, not `cygwin bash`:
```
npm install --global --production windows-build-tools
setx VCTargetsPath "%programfiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V140"
```

Then install like this:
```
npm install -g jsonld-cli
```

You may get some warnings, they seem to be harmless. Eg:
```
npm WARN deprecated request@2.88.2: request has been deprecated, see https://github.com/request/request/issues/3142
npm WARN deprecated har-validator@5.1.5: this library is no longer supported
npm WARN deprecated request-promise-native@1.0.9: request-promise-native has been deprecated because it extends the now deprecated request package, see https://github.com/request/request/issues/3142
C:\Users\...\AppData\Roaming\npm\jsonld -> C:\Users\...\AppData\Roaming\npm\node_modules\jsonld-cli\bin\jsonld
+ jsonld-cli@0.3.0
added 3 packages from 11 contributors, removed 2 packages and updated 41 packages in 18.755s
```

### Help

The builtin help `jsonld -h` is quite poor, so we dug out the options from the source https://github.com/digitalbazaar/jsonld-cli/blob/master/bin/jsonld:
```
COMMON OPTIONS
  -i, --indent <spaces>                   spaces to indent [2]
  -N, --no-newline                        do not output the trailing newline [newline]
  -k, --insecure                          allow insecure SSL connections [false]
  -t, --type <type>                       input data type [auto]
  -b, --base <base>                       base IRI []
format [options] [filename|URL|-]     format and convert JSON-LD
  -f, --format <format>                   output format [json]
  -q, --nquads                            output application/nquads [false]
  -j, --json                              output application/json [true]
compact [options] [filename|URL]      compact JSON-LD
  -c, --context <filename|URL>            context filename or URL
  -S, --no-strict                         disable strict mode
  -A, --no-compact-arrays                 disable compacting arrays to single values
  -g, --graph                             always output top-level graph [false]
expand [options] [filename|URL|-]     expand JSON-LD
      --keep-free-floating-nodes          keep free-floating nodes
flatten [options] [filename|URL|-]    flatten JSON-LD
  -c, --context <filename|URL>            context filename or URL for compaction [none]
frame [options] [filename|URL|-]      frame JSON-LD
  -f, --frame <filename|URL>              frame to use
      --embed <embed>                     default @embed flag [true]
      --explicit <explicit>               default @explicit flag [false]
      --omit-default <omit-default>       default @omitDefault flag [false]
normalize [options] [filename|URL|-]  normalize JSON-LD
  -f, --format <format>                   format to output ('application/nquads' for N-Quads)
  -q, --nquads                            use 'application/nquads' format
```
The builtin help gives the following useful advice:
- The input parameter for all commands can be a filename, a URL beginning with "http://" or "https://", or "-" for stdin (the default).
- Input type can be specified as a standard content type or a simple string for common types. See the "request" extension code for available types. XML and HTML variations will be converted with an RDFa processor if available. If the input type is not specified it will be auto-detected based on file extension, URL content type, or by guessing with various parsers. Guessing may not always produce correct results.
- Output type can be specified for the "format" command and a N-Quads shortcut for the "normalize" command. For other commands you can pipe JSON-LD output to the "format" command.

## jena riot

`jsonld-cli` can output only `nquads`, eg:

```sh
jsonld format -f text/turtle ../JSON/Example_9.6.1-ObjectEvent.jsonld > Example_9.6.1-ObjectEvent.ttl
Error: ERROR: Unknown format: text/turtle
```

So we also use `riot` from Apache Jena:
- Download: https://jena.apache.org/download/

We make a file `prefixes.ttl` that defines the same prefixes as the EPCIS context, and postprocess with `riot` to make nicely formtted Turtle
(we use the fact that the `nquads` format output by `jsonld`, when no named graphs are used, is compatible with the `ttl` format):

```sh
jsonld format -q ../JSON/Example_9.6.1-ObjectEvent.jsonld | \
  cat prefixes.ttl - | riot -syntax ttl -formatted ttl > Example_9.6.1-ObjectEvent.ttl
```

## Context Issues

All JSON/JSON-LD examples declare their own context, usually something like this (first is the EPCIS context, then some custom extensions):

```json
  "@context": ["https://gs1.github.io/EPCIS/epcis-context.jsonld",
               {"example": "http://ns.example.com/epcis/"},
               {"gs1": "https://gs1.org/voc/"}],
```

The EPCIS context is served from a Github page and corresponds to the local version [../epcis-context.jsonld](../epcis-context.jsonld) in this repository
(it may show as a smaller file because it uses NL line endings, whereas the local version uses CR+NL line endings on Windows).
This means that:
- Whenever changes are made to [../epcis-context.jsonld](../epcis-context.jsonld), it will take time until it's deployed at Github pages. 
  Furthermore, Github pages aggressively use caching, so one may still get the old context.
- The version in development [../epcis-context-protected.jsonld](../epcis-context-protected.jsonld) cannot be tested so easily.

For example, error #201 still occurs for one of the examples because 
the change `xsd:decimal -> xsd:float` is still not deployed in the context.

TODO: see if option `-c` can override the context specified in-file.
# EPCIS 2.0 JSON-LD Context

This folder contains the source code for the EPCIS 2.0 JSON-LD @context. 

The `epcis-context-root.jsonld` is the root file that has pointers to the different auxiliary children contexts that define terms corresponding to the GS1 CBV Vocabulary. 

To generate the final, single file, inlined JSON-LD @context you need to ensure you have installed the [Node.js](https://nodejs.org/en/download/) runtime. Then on the command line just execute

```
chmod +x generate-inline-context.sh
generate-inline-context.sh
```

After successfully running the script above, the single, inlined context file `epcis-context.jsonld` will be generated on the root folder of the EPCIS repository. 
# EPCIS 2.0 XSD validation

The main EPCIS v2.0 XSD draft file is [EPCglobal-epcis-2_0.xsd](EPCglobal-epcis-2_0.xsd) , which currently imports other EPCIS v1.2 XSD files which have not been altered.
Also present in this directory is an XML instance file, [SensorDataExamples.xml](../XML/WithSensorData/SensorDataExamples.xml)  which provides examples of EPCIS 2.0 event data including <sensorElementList> elements.
Thanks to @RalphTro (Ralph Troeger) for preparing the XML instance file.  Mark Harrison made a minor modification to change the attribute averagValue to mean
since there are multiple kinds of average (mean, mode, median) and if we're being really pedantic, we should probably specify that we mean the arithmetic mean rather than the geometric mean.

At present, only limited testing has been done by Mark Harrison, using Oxygen XML Editor on Mac OS.
We would all appreciate additional eyes taking a critical look at the draft [EPCglobal-epcis-2_0.xsd](EPCglobal-epcis-2_0.xsd) and providing feedback.
We need to check that all appropriate extension points from v1.2 are still supported and that the new elements introduced in v2.0 (for sensor data) also support extension.

## Change Logs

### Fixed 

- The non-deterministic behaviour of EPCIS 1.2 XSD has been fixed. EPCIS 2.0 XSD has a deterministic behavior.

### Changed

- The EPCIS 2.0 XSD gets rid of any unnecessary or duplicated extension tags. In that process Transformation Event is placed at the same level as other legacy EPCIS Events(i.e., ObjectEvent or Aggregation Events)

### Added

- The EPCIS 2.0 XSD includes all the newness in terms of feature that has been introduced in EPCIS 2.0(i.e., inclusion of sensor element and persistent disposition attribute and the addition of all new AssociationEvent in EventList).

## Test Coverage

Validated XML files against EPCIS 2.0 XSD are placed under XML directory under the root of the project. If you want to validate  your own examples then you can simply add more events and use Makefile to validate automatically.


# EPCIS 2.0 WSDL

The [EPCglobal-epcis-query-2_0.wsdl](EPCglobal-epcis-query-2_0.wsdl) supports current EPCIS 2.0 webservice definitations for SOAP XML messaging.

## Generating XML Binding using maven java code generator

For convenience and basic XML binding tests a maven [pom.xml](pom.xml) has been provided. Apache Maven and Java must be installed for running it.

```bash
mvn clean package
```

## Change Logs

- **2022-03** add maven [pom.xml](pom.xml) with JAXB (Java XML Binding) support
# EPCIS XSL Transformation Tools

Support for downscaling and upscaling between versions 1.2 and 2.0

## Background

In EPCIS 2.0, the extension wrappers around known event element is going to be removed. This can be perceived as disruptive change to implementors. This tool is built to help implementors easy migration from EPCIS 1.2 to 2.0 XML document and vice-a-versa.

## Prerequisite for tool

### Install Apache Xalan-C++

- Xalan-C++ is a fast and reliable tool for XSL Transformation. To download and install visit [https://apache.github.io/xalan-c/install.html](https://apache.github.io/xalan-c/install.html)
- xmllint

### XSL Version 2.0

To allow for more concise templates and mode based processing a XSL 2.0 transformation tool is required.
Testing an Makefile is based on the [Apache Xalan](https://xalan.apache.org) XSL toolchain.

## Running and Testing

### EPCIS 2.0 to 1.2 conversion(downscaling)

run Xalan

```bash
Xalan  ../XML/Example_9.6.1-ObjectEvent-2020_06_18a.xml ./convert-2.0-to-1.2.xsl
```

run Xalan and beautify using xmllint

```bash
Xalan  ../XML/Example_9.6.1-ObjectEvent-2020_06_18a.xml ./convert-2.0-to-1.2.xsl | xmllint --format -
```

run Xalan and validate transformation to EPCIS 1.2 using xmllint

```bash
Xalan  ../XML/Example_9.6.1-ObjectEvent-2020_06_18a.xml ./convert-2.0-to-1.2.xsl | xmllint --format - | xmllint --schema ./1.2/XSD/EPCglobal-epcis-1_2.xsd -
```
### EPCIS 1.2 to 2.0 conversion(upscaling)

run Xalan

```bash
Xalan  1.2/XML/ObjectEvent.xml ./convert-1.2-to-2.0.xsl
```

run Xalan and beautify using xmllint

```bash
Xalan  1.2/XML/ObjectEvent.xml ./convert-1.2-to-2.0.xsl | xmllint --format -
```

run Xalan and validate transformation to EPCIS 1.2 using xmllint

```bash
Xalan  1.2/XML/ObjectEvent.xml ./convert-1.2-to-2.0.xsl | xmllint --format - | xmllint --schema ../XSD/EPCglobal-epcis-2_0.xsd -
```

## EPCIS Version 1.2

To support the transformation and validation toolchain, some changes to the EPCIS 1.2 XSD had to made:

* deterministic EventListType for xmllint support (sequence of choice)
* nillable quantity in QuantityElementType

### Revised EPCIS 1.2 XSD

The following XML elements should be added to existing 1.2 extensions:

* SensorElementListType
* SensorElementType
* SensorMetadataType
* SensorReportType
* SensorElementExtensionType
* PersistentDispositionType
* AssociationEventType
* AssociationEventExtensionType

**Note** The inclusion of these elements is controlled by setting the appropriate variables in [convert-2.0-to-1.2.xsl](convert-2.0-to-1.2.xsl):

* includeSensorElementList
* includePersistentDisposition
* includeAssociationEvent
# EPCIS JSON Schemas

This folder contains the source code for the EPCIS 2.0 JSON Schema. 

The `EPCIS-JSON-Schema-root.json` is the root file that has pointers to the different auxiliary children schemas. 

To generate the final, single file, inlined JSON Schema you need to ensure you have installed 
the [Node.js](https://nodejs.org/en/download/) runtime. Then on the command line just execute

```sh
chmod +x generate-inline-schema.sh
generate-inline-schema.sh
```

After successfully running the script above, the single, inlined schema file `EPCIS-JSON-Schema.json` 
will be generated on the root folder of the EPCIS git repository. It is included to allow 
online validators to just work with one file. It contains all the Schemas defined by this specification.

For generating the EPCIS Query Schema you can

```sh
chmod +x generate-inline-query-schema.sh
generate-inline-query-schema.sh
```

After successfully running the script above, the single, inlined schema file `query-schema.json`
will be generated on the `REST API` folder of the EPCIS git repository. It is included to allow
online validators to just work with one file.

## Validation

For validating EPCIS documents the [ajv](https://www.npmjs.com/package/ajv) tool has to be installed. In addition
the [ajv-formats](https://www.npmjs.com/package/ajv-formats) plugin is also needed. Both tools can be installed using the
[npm](https://docs.npmjs.com/getting-started) package manager that works on top of a [Node.js](https://nodejs.org/en/download/) runtime. You can install both using the [nvm](https://github.com/nvm-sh/nvm#installing-and-updating) scripts. 

The `validate.sh` script allows to validate JSON and automatically includes all the individual child schemas. 

The `validate-all.sh` script allows to validate all the JSON-LD EPCIS files stored on the `JSON` folder. 
# Mktg-50anniversary
Repo for development of marketing materials around GS1 50th anniversary

## Timeline Block

Simple block for the timeline. Using the slick library (https://kenwheeler.github.io/slick/) for the creation of the block. This library can't be removed, otherwise the timeline won't work.

A working example of the timeline block can be seen at https://www.gs1.org/about/50YearsOfGS1.

### Changing the content

All images and content can be changed. We just can't remove the classes outside of that.

Examples:

- All content inside both `<div>` in the bottom can be changed but not the classes in the div:

```
<div class="wrapper">
    <img src="img/1973.png" />
</div>

...

<div class="wrapper wrapper-body">
    <h3>2022</h3>
    <p>
        A joint World Trade Organization (WTO) and World Economic
        Forum (WEF) report outlines the power of GS1 product and
        location identification to make cross-border trade more
        efficient, inclusive and sustainable.
    </p>
</div>
```# geoshapes
Experiments with geoshapes and geofences

Demo tool is available at https://gs1.github.io/geoshapes/

This folder contains a static example of the "Home Page" design
encountered in the Brand Guideline  "Sample pages" section:
https://www.notion.so/Sample-pages-0464b95b545f47d1b79fadb4636a9bb2.

All the colors define in the Brand Guideline can also be used as classes if there is a need to change the color of titles, subtitles or description fields. Example of classes: color-blue, color-orange, color-raspberry ... Brand Guideline: https://www.notion.so/gs1/GS1-global-brand-web-guidelines-6f4bb53b8833492e93f3c8de5191a568

A few classes can be used to give more or less space in between elements or sections and can be used everywhere. The classes look like this:

  - padding top spacing: pt-spacer-1, pt-spacer-2, pt-spacer-3, pt-spacer-4, pt-spacer-5, pt-spacer-6, pt-spacer-7
  - padding right spacing: pr-spacer-1, pr-spacer-2, pr-spacer-3, pr-spacer-4, pr-spacer-5, pr-spacer-6, pr-spacer-7
  - padding bottom spacing: pb-spacer-1, pb-spacer-2, pb-spacer-3, pb-spacer-4, pb-spacer-5, pb-spacer-6, pb-spacer-7
  - padding left spacing: pl-spacer-1, pl-spacer-2, pl-spacer-3, pl-spacer-4, pl-spacer-5, pl-spacer-6, pl-spacer-7

  - margin top spacing: mt-spacer-1, mt-spacer-2, mt-spacer-3, mt-spacer-4, mt-spacer-5, mt-spacer-6, mt-spacer-7
  - margin right spacing: mr-spacer-1, mr-spacer-2, mr-spacer-3, mr-spacer-4, mr-spacer-5, mr-spacer-6, mr-spacer-7
  - margin bottom spacing: mb-spacer-1, mb-spacer-2, mb-spacer-3, mb-spacer-4, mb-spacer-5, mb-spacer-6, mb-spacer-7
  - margin left spacing: ml-spacer-1, ml-spacer-2, ml-spacer-3, ml-spacer-4, ml-spacer-5, ml-spacer-6, ml-spacer-7

This folder contains a static example of the "Content" page design
encountered in the Brand Guideline  "Sample pages" section:
https://www.notion.so/Sample-pages-0464b95b545f47d1b79fadb4636a9bb2.

All the colors define in the Brand Guideline can also be used as classes if there is a need to change the color of titles, subtitles or description fields. Example of classes: color-blue, color-orange, color-raspberry ... Brand Guideline: https://www.notion.so/gs1/GS1-global-brand-web-guidelines-6f4bb53b8833492e93f3c8de5191a568

A few classes can be used to give more or less space in between elements or sections and can be used everywhere. The classes look like this:

  - padding top spacing: pt-spacer-1, pt-spacer-2, pt-spacer-3, pt-spacer-4, pt-spacer-5, pt-spacer-6, pt-spacer-7
  - padding right spacing: pr-spacer-1, pr-spacer-2, pr-spacer-3, pr-spacer-4, pr-spacer-5, pr-spacer-6, pr-spacer-7
  - padding bottom spacing: pb-spacer-1, pb-spacer-2, pb-spacer-3, pb-spacer-4, pb-spacer-5, pb-spacer-6, pb-spacer-7
  - padding left spacing: pl-spacer-1, pl-spacer-2, pl-spacer-3, pl-spacer-4, pl-spacer-5, pl-spacer-6, pl-spacer-7

  - margin top spacing: mt-spacer-1, mt-spacer-2, mt-spacer-3, mt-spacer-4, mt-spacer-5, mt-spacer-6, mt-spacer-7
  - margin right spacing: mr-spacer-1, mr-spacer-2, mr-spacer-3, mr-spacer-4, mr-spacer-5, mr-spacer-6, mr-spacer-7
  - margin bottom spacing: mb-spacer-1, mb-spacer-2, mb-spacer-3, mb-spacer-4, mb-spacer-5, mb-spacer-6, mb-spacer-7
  - margin left spacing: ml-spacer-1, ml-spacer-2, ml-spacer-3, ml-spacer-4, ml-spacer-5, ml-spacer-6, ml-spacer-7

This folder contains a static example of the "Topic Landing Page" design
encountered in the Brand Guideline  "Sample pages" section:
https://www.notion.so/Sample-pages-0464b95b545f47d1b79fadb4636a9bb2.

All the colors define in the Brand Guideline can also be used as classes if there is a need to change the color of titles, subtitles or description fields. Example of classes: color-blue, color-orange, color-raspberry ... Brand Guideline: https://www.notion.so/gs1/GS1-global-brand-web-guidelines-6f4bb53b8833492e93f3c8de5191a568

A few classes can be used to give more or less space in between elements or sections and can be used everywhere. The classes look like this:

  - padding top spacing: pt-spacer-1, pt-spacer-2, pt-spacer-3, pt-spacer-4, pt-spacer-5, pt-spacer-6, pt-spacer-7
  - padding right spacing: pr-spacer-1, pr-spacer-2, pr-spacer-3, pr-spacer-4, pr-spacer-5, pr-spacer-6, pr-spacer-7
  - padding bottom spacing: pb-spacer-1, pb-spacer-2, pb-spacer-3, pb-spacer-4, pb-spacer-5, pb-spacer-6, pb-spacer-7
  - padding left spacing: pl-spacer-1, pl-spacer-2, pl-spacer-3, pl-spacer-4, pl-spacer-5, pl-spacer-6, pl-spacer-7

  - margin top spacing: mt-spacer-1, mt-spacer-2, mt-spacer-3, mt-spacer-4, mt-spacer-5, mt-spacer-6, mt-spacer-7
  - margin right spacing: mr-spacer-1, mr-spacer-2, mr-spacer-3, mr-spacer-4, mr-spacer-5, mr-spacer-6, mr-spacer-7
  - margin bottom spacing: mb-spacer-1, mb-spacer-2, mb-spacer-3, mb-spacer-4, mb-spacer-5, mb-spacer-6, mb-spacer-7
  - margin left spacing: ml-spacer-1, ml-spacer-2, ml-spacer-3, ml-spacer-4, ml-spacer-5, ml-spacer-6, ml-spacer-7

For some reason the link in the core file https://modernizr.com/download/?-details-inputtypes-addtest-mq-prefixed-prefixes-setclasses-teststyles
always produces a 3.6.0 version when using the `Build` option.

Browse to the same URL and use the `Command Line Config` option to `Download` the config JSON file `modernizr-config.json`.

Following the instructions here https://modernizr.com/docs

```
sudo npm install -g npm
npm install -g modernizr
modernizr -c modernizr-config.json // This is the file downloaded from http://modernizr.com/download
```
This produces a `modernizr.js` file that should be renamed to `modernizr.min.js` and copied to `core/assets/vendor/modernizr/modernizr.min.js`.

Please also remember to update the version number of Modernizer in `core/core.libraries.yml`.
# Mktg-Branding-templates

Pages for use by GS1 MOs on their websites.

## To use this repository.

To use this repository, just clone the repository contents locally.

Each page is inside a self-contained folder, with all the necessary assets to
display it. Each folder has a README inside with more detailed instructions.

This folder contains a static example of the "Industry Landing Page" design
encountered in the Brand Guideline  "Sample pages" section:
https://www.notion.so/Sample-pages-0464b95b545f47d1b79fadb4636a9bb2.

All the colors define in the Brand Guideline can also be used as classes if there is a need to change the color of titles, subtitles or description fields. Example of classes: color-blue, color-orange, color-raspberry ... Brand Guideline: https://www.notion.so/gs1/GS1-global-brand-web-guidelines-6f4bb53b8833492e93f3c8de5191a568

A few classes can be used to give more or less space in between elements or sections and can be used everywhere. The classes look like this:

  - padding top spacing: pt-spacer-1, pt-spacer-2, pt-spacer-3, pt-spacer-4, pt-spacer-5, pt-spacer-6, pt-spacer-7
  - padding right spacing: pr-spacer-1, pr-spacer-2, pr-spacer-3, pr-spacer-4, pr-spacer-5, pr-spacer-6, pr-spacer-7
  - padding bottom spacing: pb-spacer-1, pb-spacer-2, pb-spacer-3, pb-spacer-4, pb-spacer-5, pb-spacer-6, pb-spacer-7
  - padding left spacing: pl-spacer-1, pl-spacer-2, pl-spacer-3, pl-spacer-4, pl-spacer-5, pl-spacer-6, pl-spacer-7

  - margin top spacing: mt-spacer-1, mt-spacer-2, mt-spacer-3, mt-spacer-4, mt-spacer-5, mt-spacer-6, mt-spacer-7
  - margin right spacing: mr-spacer-1, mr-spacer-2, mr-spacer-3, mr-spacer-4, mr-spacer-5, mr-spacer-6, mr-spacer-7
  - margin bottom spacing: mb-spacer-1, mb-spacer-2, mb-spacer-3, mb-spacer-4, mb-spacer-5, mb-spacer-6, mb-spacer-7
  - margin left spacing: ml-spacer-1, ml-spacer-2, ml-spacer-3, ml-spacer-4, ml-spacer-5, ml-spacer-6, ml-spacer-7

This folder contains a static example of the "Transactional" page design
encountered in the Brand Guideline  "Sample pages" section:
https://www.notion.so/Sample-pages-0464b95b545f47d1b79fadb4636a9bb2.

All the colors define in the Brand Guideline can also be used as classes if there is a need to change the color of titles, subtitles or description fields. Example of classes: color-blue, color-orange, color-raspberry ... Brand Guideline: https://www.notion.so/gs1/GS1-global-brand-web-guidelines-6f4bb53b8833492e93f3c8de5191a568

A few classes can be used to give more or less space in between elements or sections and can be used everywhere. The classes look like this:

  - padding top spacing: pt-spacer-1, pt-spacer-2, pt-spacer-3, pt-spacer-4, pt-spacer-5, pt-spacer-6, pt-spacer-7
  - padding right spacing: pr-spacer-1, pr-spacer-2, pr-spacer-3, pr-spacer-4, pr-spacer-5, pr-spacer-6, pr-spacer-7
  - padding bottom spacing: pb-spacer-1, pb-spacer-2, pb-spacer-3, pb-spacer-4, pb-spacer-5, pb-spacer-6, pb-spacer-7
  - padding left spacing: pl-spacer-1, pl-spacer-2, pl-spacer-3, pl-spacer-4, pl-spacer-5, pl-spacer-6, pl-spacer-7

  - margin top spacing: mt-spacer-1, mt-spacer-2, mt-spacer-3, mt-spacer-4, mt-spacer-5, mt-spacer-6, mt-spacer-7
  - margin right spacing: mr-spacer-1, mr-spacer-2, mr-spacer-3, mr-spacer-4, mr-spacer-5, mr-spacer-6, mr-spacer-7
  - margin bottom spacing: mb-spacer-1, mb-spacer-2, mb-spacer-3, mb-spacer-4, mb-spacer-5, mb-spacer-6, mb-spacer-7
  - margin left spacing: ml-spacer-1, ml-spacer-2, ml-spacer-3, ml-spacer-4, ml-spacer-5, ml-spacer-6, ml-spacer-7

# GS1 Web Vocabulary - development site

The current official version of the GS1 Web vocabualary is published at https://www.gs1.org/voc. It is an external extension to schema.org that allows further details about products and assets to be expressed using Linked Data technology. [gs1:Product](https://www.gs1.org/voc/Product) is semantically equivalent to [schema:Product](http://schema.org/Product). The GS1 Web vocabulary also defines subclasses of [gs1:Product](https://www.gs1.org/voc/Product)

The GS1 Web vocabulary is released under an Apache 2.0 licence. A further licence statement is provided within the GS1 Web vocabulary files.
 
This repository is intended to encourage suggestions for improvements to the GS1 Web Vocabulary. Please note the license terms (Apache 2.0). 

Files in this repository are arranged as follows.

 * An immutable copy of each ratified version of the GS1 Web Vocabulary is stored in a directory that gives the version number. 
 * There is a copy of the current version provided in the root directory so there is a stable URI from which the current version can be obtained, in addition to the formally published version on gs1.org. In case of any discrepency, the formally published version at https://www.gs1.org/voc/ is authoritative. 
 * There is a 'patch' file that just contains informally proposed terms.
 * A copy of the current file plus the patch is also included.
 * Each file is made available in both Turtle and JSON-LD. 
 
 Most terms within the GS1 Web vocabulary can usually be classified as one of the following:

* [Classes](#classes)
* [Properties](#properties)
* [Code Lists](#code-lists)
* [Defined values within Code Lists](#code-list-values)
* [Link Types](#link-types)


## Classes

One use of a class (rdfs:Class, owl:Class) is to express an entity such as a product, organization, place, postal address.

Another use of a class is to provide a repeatable data structure as a container for a number of interdependent properties.

For example, a [gs1:QuantitativeValue](https://www.gs1.org/voc/QuantitativeValue)  or [schema:QuantitativeValue](http://schema.org/QuantitativeValue) express both a numeric value and a code for a unit of measure.  

Similarly, [gs1:CertificationDetails](https://www.gs1.org/voc/CertificationDetails) is used to group interdependent properties such as [gs1:certificationAgency](https://www.gs1.org/voc/certificationAgency) , [gs1:certificationStandard](https://www.gs1.org/voc/certificationStandard) and [gs1:certificationValue](https://www.gs1.org/voc/certificationValue) so that when a product has more than one certification, there is no ambiguity about which standard was evaluated by which agency - or which value was obtained for each standard.

Some classes are defined as subclasses of other classes.

For example, 

[gs1:FoodBeverageTobaccoProduct](https://www.gs1.org/voc/FoodBeverageTobaccoProduct) is a subclass of [gs1:Product](https://www.gs1.org/voc/Product)

[gs1:FruitsVegetables](https://www.gs1.org/voc/FruitsVegetables) is a subclass of [gs1:FoodBeverageTobaccoProduct](https://www.gs1.org/voc/FoodBeverageTobaccoProduct)

By defining subclasses, we can 'attach' more specialised properties that are relevant to the subclass but not generally relevant to all members of the parent class / superclass.

[Browse all classes within the GS1 Web vocabulary](https://www.gs1.org/voc/?show=classes)

## Properties
Each property has an expected value type (indicated via rdfs:range)

Each property also has an 'attachment point' (indicated via rdfs:domain)

A property that could apply to all kinds of products will generally have an rdfs:domain of [gs1:Product](https://www.gs1.org/voc/Product) / [schema:Product](http://schema.org/Product)

Other properties that are only really relevant to a more specialised category of products will have an rdfs:domain that is a subclass of [gs1:Product](https://www.gs1.org/voc/Product) (such as [gs1:WearableProduct](https://www.gs1.org/voc/WearableProduct) ) or even a subclass of a subclass of [gs1:Product](https://www.gs1.org/voc/Product) (such as [gs1:Footwear](https://www.gs1.org/voc/Footwear) )

For example, 

[gs1:isSeedless](https://www.gs1.org/voc/isSeedless) is a property of [gs1:FruitsVegetables](https://www.gs1.org/voc/FruitsVegetables) - and it probably has little relevance to any other kind of product.

Formally, the GS1 Web vocabulary expresses that [gs1:isSeedless](https://www.gs1.org/voc/isSeedless) has an rdfs:domain of [gs1:FruitsVegetables](https://www.gs1.org/voc/FruitsVegetables).

[Browse all properties within the GS1 Web vocabulary](https://www.gs1.org/voc/?show=properties)

## Code Lists
The GS1 Web vocabulary defines a large number of code lists for enumerated values.
Code lists are useful because a globally defined URI can be used for each permitted value.  Each of these URIs may have multilingual labels and descriptions in different human languages but we agree to use the global URI to express the value, to avoid the need to translate 'free text' values expressed in different human languages when exchanging data globally using such code lists.

Each code list is modelled as a class (rdfs:Class, owl:Class) and as a subclass of [gs1:TypeCode](https://www.gs1.org/voc/TypeCode), the abstract superclass for all GS1 Code Lists within the GS1 Web vocabulary.

For example,
[gs1:SharpnessOfCheeseCode](https://www.gs1.org/voc/SharpnessOfCheeseCode) is a subclass of [gs1:TypeCode](https://www.gs1.org/voc/TypeCode)

[Browse all code lists within the GS1 Web vocabulary](https://www.gs1.org/voc/?show=typecodes)


## Code list values
Each defined value within a code list has its own Web URI and may have multilingual human labels and descriptions.  Membership of a particular code list is indicated via rdf:type

For example,
[gs1:SharpnessOfCheeseCode-EXTRA_SHARP](https://www.gs1.org/voc/SharpnessOfCheeseCode-EXTRA_SHARP) is an individual code value within the [gs1:SharpnessOfCheeseCode](https://www.gs1.org/voc/SharpnessOfCheeseCode) code list.

Its rdf:type is [gs1:SharpnessOfCheeseCode](https://www.gs1.org/voc/SharpnessOfCheeseCode), the code list to which it belongs.

## Link Types
The GS1 Web vocabulary introduced a group of additional properties that connect a [GS1 Digital Link](https://www.gs1.org/standards/gs1-digital-link) URI to a target resource URL, such as a product information page, instruction manual, related video, electronic patient information leaflet for a pharmaceutical etc.  

Each link type property expresses a distinct kind of information resource found at the target resource URL.  

In this way, a Web request to a resolver for [GS1 Digital Link](https://www.gs1.org/standards/gs1-digital-link) URI can specify a particular kind of information resource that is desired, e.g. 'give me the instruction manual'.  The Link Type is typically expressed as a compact URI expression (CURIE) within the URI query string, as the value of the special 'linkType' key.  It is also expressed in the linkset of results returned by a resolver conforming to the [GS1 Digital Link standard](https://www.gs1.org/standards/gs1-digital-link).

The GS1 Web vocabulary defines one abstract property, [gs1:linkType](https://www.gs1.org/voc/linkType).  

All specific link type values are defined as a subproperty of [gs1:linkType](https://www.gs1.org/voc/linkType).

For example,
[gs1:instructions](https://www.gs1.org/voc/instructions) is a subproperty of [gs1:linkType](https://www.gs1.org/voc/linkType)  

[gs1:instructions](https://www.gs1.org/voc/instructions) is a typed link that is used to link to instructions related to the product, such as assembly instructions, usage tips etc.

[Browse all link types defined within the GS1 Web vocabulary](https://www.gs1.org/voc/?show=linktypes)
GS1 Barcode Syntax Engine
=========================

The GS1 Barcode Syntax Engine ("Syntax Engine") is a library that supports the processing of
GS1 syntax data, including Application Identifier element strings and GS1
Digital Link URIs. It includes a native C library together with bindings
for C# .NET, Java and Swift, that is intended to be integrated into a wide
variety of platforms.

The project also serves as a reference implementation of a framework for
processing the [GS1 Barcode Syntax Dictionary](https://ref.gs1.org/tools/gs1-barcode-syntax-resource/syntax-dictionary/)
and its subordinate [GS1 Barcode Syntax Tests](https://ref.gs1.org/tools/gs1-barcode-syntax-resource/syntax-tests/).

This project includes:

  * A C library that can be:
    * Vendored into third-party code.
    * Compiled to native code for use as a shared library (Linux / MacOS / BSD) or dynamic-link library (Windows).
    * Compiled to WebAssembly or pure JavaScript for use in a browser-based web application or Node.js application.
  * A C# .NET wrapper class that provides an object interface to the native library from managed code, using Platform Invoke (P/Invoke).
  * A Java wrapper class that provides an object interface to the native library from managed code, using Java Native Interface.
  * Several example applications:
    * A console application whose C code shows how to use the native library.
    * A console application whose Java code shows how to use the Java Native Interface wrapper.
    * A desktop application using Windows Presentation Foundation (WPF) whose code shows how to use the C# .NET wrapper.
    * A browser-based web application that shows how to use the WebAssembly or pure JavaScript build of the library.
    * A Node.js console application that shows how to use the WebAssembly or pure JavaScript build of the library.
    * An Android Studio project that shows how to use the Java wrapper from Kotlin to create an Android app that includes support for decoding GS1 data in barcodes scanned using ML Kit.
    * An Xcode project that shows how to use the native library from Swift to create an iOS app that includes support for decoding GS1 data in barcodes scanned using ML Kit.


Documentation
-------------

The C library API is fully documented in the docs/ directory and is
available online here: <https://gs1.github.io/gs1-syntax-engine/>

Instructions for getting started with the console application are provided in
the [Console Application User Guide](https://github.com/gs1/gs1-syntax-engine/wiki/Console-Application-User-Guide).

Instructions for getting started with the desktop application are provided in
the [Desktop Application User Guide](https://github.com/gs1/gs1-syntax-engine/wiki/Desktop-Application-User-Guide).


Using the library
------------------

The library is provided with full source and also in the form of a pre-built
library (portable DLL) along with associated development headers (.h) and
linker (.lib) files.

Pre-built assets are available here:

<https://github.com/gs1/gs1-syntax-engine/releases/latest>

The license is permissive allowing for the source code to be vendored into an
application codebase (Open Source or proprietary) or for the pre-built shared
library to be redistributed with an application.

This repository contains:

| Directory      | Purpose                                                                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| src/c-lib      | Source for the native C library ("The library"), unit tests, fuzzers and demo console application                                               |
| docs           | Documentation for the public API of the native C library                                                                                        |
| src/dotnet-lib | C# .NET wrappers that provide a managed code interface to the native library using P/Invoke                                                     |
| src/dotnet-app | A demo C# .NET desktop application (WPF) that uses the wrappers and native library                                                              |
| src/js-wasm    | A JavaScript wrapper that provides an developer-friendly interface to the WASM or pure JavaScript build, with demo web and console applications |
| src/java       | A Java wrapper that provides a managed code interface to the native library using Java Native interface                                         |
| src/android    | An Android Studio project that demonstrates how to use the Java wrapper from Kotlin to create an Android app                                     |
| src/ios        | An Xcode project that demonstrates how to use the native library from Swift to create an iOS app                                                |


### Building on Windows

The library, wrappers, demonstration console application and demonstration
desktop application can be rebuilt on Windows using MSVC.

The project contains a solution file (.sln) compatible with recent versions of
Microsoft Visual Studio. In the Visual Studio Installer you will need to ensure
that MSVC is installed by selecting the "C++ workload" and that a recent .NET
Core SDK is available. You must build using the "`x86`" solution platform.

Alternatively, all components can be built from the command line by opening a
Developer Command Prompt, cloning this repository, changing to the `src`
directory and building the solution using:

    msbuild /p:Configuration=release gs1encoders.sln


### Building on Linux or MacOS

The library and demonstration console application can be rebuilt on any Linux
or macOS system that has a C compiler (such as GCC or Clang).

To build using the default compiler change into the `src/c-lib` directory and run:

    make

A specific compiler can be chosen by setting the CC argument for example:

    make CC=gcc

    make CC=clang


#### Development targets

There are a number of other targets that are useful for library development
purposes:

    make test [SANITIZE=yes]  # Run the unit test suite, optionally building using LLVM sanitizers.
    make fuzzer               # Build fuzzers for exercising the individual encoders. Requires LLVM libfuzzer.


#### JavaScript / WASM build

The WASM build artifacts can be generated by first installing and activating
the Emscripten SDK and then running:

    make wasm [JSONLY=yes]    # Set JSONLY=yes to create a JS-only build that does not use WebAssembly.

Alternatively, on a Docker-enabled system a WASM / JS-only build can be
launched from the project home directory with:

    docker run --rm -v $(pwd):/src -u $(id -u):$(id -g) emscripten/emsdk  make -C src/c-lib wasm [JSONLY=yes]


#### Java wrapper

The Java wrapper for the Syntax Engine can be built by first compiling the
Syntax Engine C library as a static library, and then building the wrapper
itself:

    make -C src/c-lib -j `nproc` libstatic
    ant -f src/java/build.xml test

To use the wrapper in a Java project it is sufficient to place the generated
`src/java/libgs1encoders.{jar,so}` files into accessible locations, then:

  * At compile time and runtime, add the .jar file into the project's
    classpath.
  * At runtime, add the directory containing the .so file into
    `java.library.path`.


Installing the Pre-built Demo Console Application
-------------------------------------------------

A demonstration console application is provided in the form of an .EXE file
compatible with modern 64-bit Windows operating systems and as a .bin file
compatible with 64-bit Linux operating systems. There are no installation
dependencies and the file can be run from any location on the file system.

The most recent version of the console application can be
[downloaded from here](https://github.com/gs1/gs1-syntax-engine/releases/latest).

For Windows systems download the asset named
`gs1encoders-windows-console-app.zip`. For Linux systems download the asset
named `gs1encoders-linux-app.zip`. In the event of issues with antivirus software
consult the note in the
[User Guide](https://github.com/gs1/gs1-syntax-engine/wiki/Console-Application-User-Guide).

The pre-built application requires that the Visual C++ Redistributable 2019 (32
bit) is installed: <https://visualstudio.microsoft.com/downloads/#microsoft-visual-c-redistributable-for-visual-studio-2019>


Installing the Pre-built Demo Desktop Application
-------------------------------------------------

A demonstration desktop application is provided in the form of an .EXE file
compatible with modern 64-bit Windows operating systems and a recent .NET
Framework.

The most recent version of the desktop application can be
[downloaded from here](https://github.com/gs1/gs1-syntax-engine/releases/latest).

For Windows systems download the asset named `gs1encoders-windows-gui-app.zip`. In
the event of issues with antivirus software consult the note in the
[User Guide](https://github.com/gs1/gs1-syntax-engine/wiki/Desktop-Application-User-Guide).

The pre-built application requires that the .NET Core 3.1 Desktop Runtime -
Windows x86 is installed: <https://dotnet.microsoft.com/download/dotnet/3.1/runtime>


Installing the Pre-built Demo Web Browser Application and Node.js Application
-----------------------------------------------------------------------------

A demonstration build, that can be run as either a web browser application or a
Node.js console application, is provided in two flavours:

1. A compilation to a WebAssembly executable with supporting JavaScript loader
2. A transpilation to pure JavaScript ("asm.js") with associated mem file

Each of these flavours includes the JavaScript wrapper (providing the user API)
and HTML / JS / Node.js implementation files. They are compatible with all modern
web browsers and any maintained release of Node.js.

The most recent version can be
[downloaded from here](https://github.com/gs1/gs1-syntax-engine/releases/latest).

Download the asset named `gs1encoders-wasm-app.zip` or `gs1encoders-jsonly-app.zip`
based on the required flavour (WASM or pure JavaScript, respectively).

To use the demo web application, extract the ZIP file and place the resulting files
in a single directory to be served by a web server as static content. Simply point a
WebAssembly-enabled browser at the HTTP location of the `.html` file and the web
application will load.

Note: For the WASM build, ensure that the web server is configured to serve the
`.wasm` file with the MIME type `application/wasm`.

To use the demo Node.js console application, extract the ZIP file into a single
directory and start it by running the following from within the same directory:

    node example.node.mjs

Maintenance Notes
=================

These notes are intended for project maintainers, not regular users of the library.


Release Procedure
-----------------

Sync with latest Syntax Dictionary release

  - Ensure that a version is tagged in the gs1-syntax-dictionary.txt file.
  - Freshen the embedded AI table.
    - `cd src/c-lib && cat gs1-syntax-dictionary | ./build-embedded-ai-table.pl > aitable.inc`


Sanity checks:

```
make -C src/c-lib clean-test
make -C src/c-lib test SANITIZE=yes
make -C src/c-lib fuzzer
[ Run them. ]
```


Freshen copyright notices:

```
make -C src/c-lib copyright
```


Update CHANGES file, ensursing that the correct project version is set:

```
editor CHANGES
[ Finalise entry for new version ]

VERSION=$(egrep -m1 '^[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+$' CHANGES)
echo "$VERSION"
```


Tag a release and push:

```
git tag "$VERSION"
git push origin "$VERSION"
git push gs1 "$VERSION"
```

Manually update the release notes.


Align node.js and Java package versions with project version.

```
make -C src/c-lib setversion
```


Build and publish the npm package:

```
make -C src/c-lib clean-wasm
docker run --rm -v $(pwd):/src -u $(id -u):$(id -g) emscripten/emsdk make -C src/c-lib wasm
cd src/js-wasm
npm install
npm test
npm pack
npm publish
```

gs1encoder
==========

JavaScript wrapper library for the GS1 Barcode Syntax Engine compiled as a WASM by
Emscripten.

This JS library is provided as an ESM and therefore requires a modern Node.js engine.


Documentation
-------------

The library is a lightweight wrapper around the Syntax Engine native C library described here:
<https://gs1.github.io/gs1-syntax-engine/>


Example
-------

A minimal example is as follows:

```shell
npm init es6
...
npm install --save gs1encoder
```

`example.js`:

```javascript
import { GS1encoder } from "gs1encoder";

var gs1encoder = new GS1encoder();
await gs1encoder.init();

console.log("\nSyntax Engine version: %s\n", gs1encoder.version);

gs1encoder.aiDataStr = "(01)09521234543213(99)TESTING123";

console.log("AI element string:              %s", gs1encoder.aiDataStr);
console.log("Barcode message:                %s", gs1encoder.dataStr);
console.log("Canonical GS1 Digital Link URI: %s", gs1encoder.getDLuri(null));

gs1encoder.free();
```

```shell
$ node example.js

Syntax Engine version: Apr  6 2024

AI element string:              (01)09521234543213(99)TESTING123
Barcode message:                ^010952123454321399TESTING123
Canonical GS1 Digital Link URI: https://id.gs1.org/01/09521234543213?99=TESTING123
```

An comprehensive, interactive example is provided here:
<https://github.com/gs1/gs1-syntax-engine/blob/main/src/js-wasm/example.node.mjs>
# GS1 Scan4Transport (S4T)
Scan4Transport (S4T) interactive demo page is at https://gs1.github.io/S4T/

Mobile decoder demo (with QR scanning using https://github.com/cozmo/jsQR toolkit ) is at https://gs1.github.io/S4T/mobile.htm

If you have suggestions for improvements or would like to collaborate in this repository, please contact mark.harrison@gs1.org and phil.archer@gs1.org
# geocode
[GSCN 21-318](https://www.gs1.org/docs/barcodes/GSCN_21-318_GSCN_Geo-coordinates.pdf) will introduce into the next edition of GS1 General Specifications a new GS1 Application Identifier (4309) for Ship-to / Deliver-to Geocode.  The expected value is a 20-digit numeric string that encodes WGS84 latitude/longitude coordinates with a precision of around 1.1 centimetres.  This is expected to be useful to support the delivery of parcels and logistic units that do not have a conventional postal address.

A demo page is available at https://gs1.github.io/geocode/

Within a barcode, an all-numeric geocode can be encoded more efficiently than a code that requires symbol characters such as + or - or decimal point or alphabetic characters such as N, S, E, W.

Using 20 numeric digits it is possible to encode WGS84 latitude/longitude coordinates with a precision of around 1.1 centimetres.

That's because 0.0000001 degrees corresponds to approximately 1.1cm  on the surface of the Earth (2&pi; * 6371,000m / 1E7 / 360.

In this approach we use two 10 digit fields that are concatenated together to form a 20-digit numeric geocode string.  

The first ten digits represent latitude measured in decimal degrees northwards from the goegraphic south pole, then multiplied by 10 million and (if necessary) left-padded with '0' digits to reach a total of 10 digits.  This approach means that the value is always positive, ranging from 0 at the geographic south pole to 1800000000 at the geographic north pole.

The second ten digits represent longitude measured in decimal degrees east of the Greenwich meridian, then multiplied by 10 million.  Locations west of the Greenwich meridian (such as the Hallgrímskirkja in Reykjavik, Iceland) might be considered to have a negative longitude such as -21.926538572471713 but by adding 360°, this can be expressed as a positive longitude such as +338.0734614275.  It is this positive longitude value in decimal degrees that is then multiplied by 10 million and (if necessary) left-padded with '0' digits to reach a total of 10 digits.

The following diagrams provide some further explanation of this approach:

![Latitude and longitude](GeoCodeIntroPage.svg?raw=true "Latitude and longitude")

Flowchart for encoding latitude and longitude as a 20-digit geocode:

![Encoding flowchart](Flowchart1.svg?raw=true "Flowchart for encoding")

Flowchart for decoding a 20-digit geocode to latitude and longitude:

![Decoding flowchart](Flowchart2.svg?raw=true "Flowchart for decoding")

Summary of formulae:

![Formulae summary](Summary.svg?raw=true "Summary of formulae")

Worked Example 1:

![Worked example 1](WorkedExample1.svg?raw=true "Worked example 1")

Worked Example 2:

![Worked example 2](WorkedExample2.svg?raw=true "Worked example 2")







# GS1 Digital Link, conformant resolvers and more #
For several years, this repo served as a quick start guide for GS1 Digital Link. It has now been superseded by other documents and resources and so most of the content that was here has been removed. The links below should provide what you're looking for;

* The [Quick start guide for GS1 Digital Link](https://ref.gs1.org/docs/2024/digital-link-quick-start-guide) is written for technical staff who have been given the task of "implementing GS1 Digital Link."
* [Connecting barcodes to related information](https://ref.gs1.org/docs/2024/connecting-barcodes-to-related-information) is a general discussion of how you might manage the task of linking a single GS1 barcode to multiple sources of relevant information. It builds on [Best practices for creating your QR Code powered by GS1](https://ref.gs1.org/docs/2023/QR-Code_powered-by-GS1-best-practices).
* [The Barcode Syntax Resource](https://ref.gs1.org/tools/gs1-barcode-syntax-resource/) is a set of production-grade open source tools that allow you to work with GS1 identifiers and barcodes, including those using GS1 Digital Link URI syntax. It includes libraries for use in iOS and Android apps.
* The [GS1 Digital Link URI Syntax](https://ref.gs1.org/standards/digital-link/uri-syntax/) and [GS1-Conformant resolver](https://ref.gs1.org/standards/resolver/) standards are the normative documents.

## Other resources ##
* There's a [9 minute video](https://youtu.be/H2idDJeH3o4) that provides an introduction to the different layers that comprise GS1 Digital Link. This predates the time when the GS1-Conformant resolver was separated out from the original GS1 Digital Link standard but is a useful intro to the concepts. This is complemented by a paper written in 2020 [11 Transferable Principles from GS1 Digital Link](https://gs1.github.io/DigitalLinkDocs/principles/).

## The GS1 Global Office resolver ##
The resolver at `id.gs1.org` operates under strict rules to ensure that any links returned are approved by the brand owner (see the [terms of use](https://www.gs1.org/standards/resolver/terms-of-use)). A staging environment is available. 

## More information ##
For more information, please contact your local [GS1 Member Organisation](https://www.gs1.org/contact).

# 11 Transferable Principles of GS1 Digital Link
This repository supports the publication of the [11 Transferable Principles of GS1 Digital Link](https://gs1.github.io/DigitalLinkDocs/principles/) which is designed to promote those principles in other standards work outside GS1.

Please note that the images in this directory were obtained from Flickr and are used under Creative Commons licensing. Please see the primary document (the index.html file) for details.
