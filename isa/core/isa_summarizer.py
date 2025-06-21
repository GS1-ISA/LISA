# isa_summarizer.py

def summarize_changes(files_touched):
    """
    Generates a summary of changes made across multiple files.
    This is a placeholder and will be expanded with actual summarization logic.
    """
    summary = f"Changes detected across {len(files_touched)} files:\n"
    for file in files_touched:
        summary += f"- {file}\n"
    return summary

if __name__ == "__main__":
    # Example usage (for testing purposes)
    test_files = ["file1.py", "file2.js", "file3.md"]
    print(summarize_changes(test_files))