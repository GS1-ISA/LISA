export function schemaDiffAnalyzer(oldSchema: any, newSchema: any): string {
  const diffs: string[] = [];
  for (const key in newSchema) {
    if (!(key in oldSchema)) diffs.push(`Added field: ${key}`);
  }
  for (const key in oldSchema) {
    if (!(key in newSchema)) diffs.push(`Removed field: ${key}`);
  }
  return diffs.join("\n");
}
