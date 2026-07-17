import { readFile, writeFile } from "node:fs/promises";
import { URL } from "node:url";

import openapiTS, { astToString } from "openapi-typescript";
import { factory } from "typescript";

const SCHEMA_URL = "http://localhost:8000/openapi.json";
const SCHEMA_FILE = process.env.OPENAPI_FILE;
const OUT = "src/api/schema.gen.ts";

const BLOB = factory.createTypeReferenceNode(factory.createIdentifier("Blob"));

const source = SCHEMA_FILE
  ? JSON.parse(await readFile(SCHEMA_FILE, "utf8"))
  : new URL(SCHEMA_URL);

const ast = await openapiTS(source, {
  transform(schemaObject) {
    if (schemaObject.format === "binary") return BLOB;
  },
});

await writeFile(OUT, astToString(ast));
