int git_commit_amend(
    git_oid *id,
    const git_commit *commit_to_amend,
    const char *update_ref,
    const git_signature *author,
    const git_signature *committer,
    const char *message_encoding,
    const char *message,
    const git_tree *tree);
