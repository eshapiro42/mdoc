# mdoc
### Modular documents

With mdoc you can create recursive, modular documents. It has three main feature:

1. It lets you include entire files in other documents.
2. It lets you include snippets of files in other documents.
3. It lets you use externally defined variables throughout your documents.

That's the 'modular' part. The 'recursive' part means that the included documents can themselves include other documents, ad infinitum.

For example, this readme was generated from the various pieces sitting in the ```readme``` directory.

## mdoc tags

mdoc accomplishes all of this by parsing your input files for mdoc tags. These tags look like:

1. ```{mdoc include file.ext}``` <-- to include the file ```file.ext```
2. ```{mdoc include tag eq1 from file.ext}``` <-- to include the snippet called ```eq1``` from the file ```file.ext```
3. ```{mdoc var1}``` <-- to insert the variable called ```var1```

You might be wondering how, if this readme is generated using mdoc, I was able to type {mdoc ...} above without it being parsed. This is thanks to the ```static``` option, which prevents included files from being parsed and includes them verbatim:

* ```{mdoc include file.ext static}``` <-- includes ```file.ext``` but does not parse it for mdoc tags
* ```{mdoc include tag eq1 from file.ext static}``` <-- includes snippet ```eq1``` from ```file.ext``` but does not parse it for mdoc tags

There is no static option for variables, since that wouldn't make any sense.

Snippets are defined as follows:

```
{mdoc tag snippet_name}
...
snippet contents
...
{mdoc untag snippet_name}
```

You can then reference the snippet name and the file it lives in to include it in another document. This is very handy for including snippets of code that may change over time, as well as other fluctuating content.


## usage

Using mdoc is simple, once you've installed it. Simply navigate into the folder where your main document template lives and run:

```
mdoc --input <INPUT_DOCUMENT> --output <OUTPUT_DOCUMENT> --variables <VARIABLES_JSON>
```

This will parse INPUT_DOCUMENT, insert any variables defined in VARIABLES_JSON, and spit out OUTPUT_DOCUMENT.

If you do not wish to generate an output file and simply want to see what the output would look like, you can replace the ```--output <OUTPUT_DOCUMENT>``` with ```--dryrun```.

If you've lost track of all the variables needed throughout your documents, you can use ```--showvariables``` rather than ```--output``` or ```--dryrun``` and it will spit out a JSON-formatted list of all the variables you need. You can pipe this into a file to make things really easy!

```
mdoc --input <INPUT_DOCUMENT> --showvariables > <VARIABLES_JSON>
```
