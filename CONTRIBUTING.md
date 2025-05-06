# GitHub Workflow & Contribution Guidelines

This document outlines the GitHub workflow and contribution standards for the "Group A - Record Management System" project. Adhering to these guidelines is crucial for maintaining a clean, understandable, and efficient development process, especially given our 2-week timeline.

**Project Repository:** [https://github.com/Bondok-devo/group-a-record-management-system.git](https://github.com/Bondok-devo/group-a-record-management-system.git)

## 1. Branching Strategy

We will use a streamlined Gitflow-like model:

* **`main` branch:**
    * Represents the most stable, submission-ready version.
    * **Direct pushes to `main` are prohibited.** Protected branch.
    * Code is merged into `main` **only** from `develop` by the Project Manager (PM) before submission.

* **`develop` branch:**
    * Our primary integration branch. All completed features/fixes merge here first.
    * Should always aim to be in a working state.
    * Feature branches are created *from* `develop` and merged back *into* `develop`.

* **Feature branches (`feature/<descriptive-name>`):**
    * All new development **must** be done in a dedicated feature branch.
    * Branch names should be lowercase, hyphenated, and prefixed with `feature/`.
    * Examples: `feature/client-gui-form`, `feature/backend-flight-crud`, `feature/json-save-load`.
    * **How to create a feature branch:**
        ```bash
        # Ensure you are on the develop branch and it's up-to-date
        git checkout develop
        git pull origin develop

        # Create and switch to your new feature branch
        git checkout -b feature/your-new-feature-name
        ```

* **Bugfix branches (`fix/<descriptive-name>`):** (Use as needed)
    * For dedicated fixes of bugs found in the `develop` branch.
    * Branch names prefixed with `fix/`. Example: `fix/client-id-uniqueness`.
    * Create fix branches from `develop` and merge them back into `develop` via Pull Request.

## 2. Commit Messages

We will **strictly follow** the commit message standard outlined in the [PyInstaller Guidelines for Commits](https://pyinstaller.org/en/stable/development/guidelines-for-commits.html). This is a project requirement.

* **Format:**
    ```
    <type>: <subject>

    [optional body: more detailed explanation, if needed]

    [optional footer: e.g., "Closes #issue_number"]
    ```

* **Allowed `<type>` values:**
    * `feat`: A new feature for the user.
    * `fix`: A bug fix for the user.
    * `docs`: Changes to documentation only.
    * `style`: Formatting, missing semi-colons, etc.; no production code change.
    * `refactor`: Refactoring production code, e.g., renaming a variable; no new features or bug fixes.
    * `test`: Adding missing tests, refactoring tests; no production code change.
    * `chore`: Updating build tasks, package manager configs, etc.; no production code change.

* **`<subject>` rules:**
    * Written in the **imperative mood** (e.g., "Add login screen" NOT "Added login screen").
    * Concise (max 50 characters recommended).
    * No period (`.`) at the end.

* **Examples:**
    ```
    feat: Implement client data entry form
    ```
    ```
    fix: Correct flight record deletion logic
    ```
    ```
    docs: Update README with GitHub workflow
    ```
    ```
    test: Add unit tests for data_manager CRUD functions
    ```

* **Commit Frequency:** Make small, logical, atomic commits. Each commit should represent a single, self-contained change.

## 3. Pull Requests (PRs)

* All `feature/*` and `fix/*` branches **must be merged into `develop` via a Pull Request (PR)** on GitHub. Never merge directly into `develop` locally and push.
* **Creating a PR:**
    1.  Push your completed feature/fix branch to GitHub: `git push -u origin feature/your-feature-name`.
    2.  Go to the project's GitHub repository page and click the "Compare & pull request" button for your branch.
    3.  Ensure the base branch is `develop` and the compare branch is your feature/fix branch.
    4.  Write a clear PR title (often reflects the main commit message) and description (summarize changes, purpose, link related issues using "Closes #issue_number").
* **Review Process:**
    1.  Notify the team (e.g., in your group chat) that your PR is ready for review.
    2.  At least **one other team member** must review the PR. Assign a reviewer if needed.
    3.  **Reviewers should check for:** Code clarity, correctness, adherence to standards, functionality (pull branch locally and test if possible), proper commit messages, sufficient tests, potential bugs.
    4.  Provide feedback using GitHub's review tools (comments, suggestions, approval).
* **Addressing Feedback:** The PR author **must** address all review comments/requests. Make additional commits to the same feature branch (they will automatically update the PR).
* **Merging a PR:**
    1.  Once the PR is approved and discussions are resolved, it can be merged.
    2.  The **Project Manager (PM)** or a designated lead will perform the merge into `develop`.
    3.  Use "Squash and merge" (preferred for clean history) or "Create a merge commit".
    4.  Delete the source branch (feature/fix branch) after merging (GitHub provides a button for this).

## 4. General Workflow Summary

1.  **Sync `develop`:** Before starting work, update your local `develop`:
    ```bash
    git checkout develop
    git pull origin develop
    ```
2.  **Create Feature Branch:** Create your branch from the up-to-date `develop`:
    ```bash
    git checkout -b feature/my-new-task
    ```
3.  **Develop & Commit:** Work on your task. Make frequent, small commits with proper messages.
4.  **Push & Create PR:** Once the feature is complete and tested locally:
    ```bash
    git push -u origin feature/my-new-task
    ```
    Go to GitHub and create a Pull Request targeting the `develop` branch.
5.  **Review & Merge:** Participate in the code review process. Address feedback. Get the PR approved and merged by the PM/lead.
6.  **Repeat:** Sync `develop` again before starting the next task.

## 5. GitHub Issues

* Use GitHub Issues actively to track:
    * comments and short discussions for documentation reasons
    * Long discussions should remain on MS Teams
* Use labels (`bug`, `feature`, `gui`, `backend`, `documentation`, `priority-high`, etc.) for organization.
* Reference issue numbers in commit messages (optional body/footer) or PR descriptions (e.g., `Closes #23`, `Refs #45`).

---

Adhering to these standards will help us collaborate effectively and deliver a successful project. Please ensure you understand and follow this workflow.