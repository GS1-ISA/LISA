#!/bin/bash

cd /Users/frisowempe/ISA_D/gs1_research

repos=(
"gs1-syntax-engine"
"GS1DigitalLicenses"
"gs1-syntax-dictionary"
"vc-data-model-verifier"
"TDT"
"EUDR-tool"
"GS1DL-resolver-testsuite"
"GS1_DigitalLink_Resolver_CE"
"interpretGS1scan"
"GS1DigitalLinkCompressionPrototype"
"linkset"
"GS1DigitalLinkToolkit.js"
"moduleCount"
"DigitalLinkDocs"
"WebVoc"
"EPCIS"
"exampleGTIN"
"gmn-helpers"
"gs1-digital-link-uri-simple-parser"
"2d-barcode-generator"
"VC-Data-Model"
"geoshapes"
"S4T"
"Mktg-50anniversary"
"digital-link.js"
"dalgiardino"
"Mktg-Branding-templates"
"vbg-l2sd-demo"
"geocode"
"EndToEndTraceability"
"UnitConverterUNECERec20"
)

for repo in "${repos[@]}"
do
  git clone https://github.com/gs1/$repo.git
done