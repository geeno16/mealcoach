import { writeFile } from "node:fs/promises";
import { URL } from "node:url";

import openapiTS, { astToString } from "openapi-typescript";
import { factory } from "typescript";

const SCHEMA_URL = "http://localhost:8000/openapi.json";
const OUT = "src/api/schema.gen.ts";

const BLOB = factory.createTypeReferenceNode(factory.createIdentifier("Blob"));

const ast = await openapiTS(new URL(SCHEMA_URL), {
  transform(schemaObject) {
    if (schemaObject.format === "binary") return BLOB;
  },
});

await writeFile(OUT, astToString(ast));
