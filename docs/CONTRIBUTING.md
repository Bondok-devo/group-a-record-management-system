# GitHub Workflow & Contribution Guidelines

This document outlines the GitHub workflow and contribution standards for the "Group A - Record Management System" project. Adhering to these guidelines is crucial for maintaining a clean, understandable, and efficient development process, especially given our 2-week timeline.

**Project Repository:** [https://github.com/Bondok-devo/group-a-record-management-system.git](https://github.com/Bondok-devo/group-a-record-management-system.git)

## 1. Branching Strategy

We will use a streamlined Gitflow-like model. All development, fixes, and tasks must be done in dedicated branches created from `develop`. Branch names should be lowercase, hyphenated, and clearly prefixed according to their purpose.

* **`main` branch:**
    * Represents the most stable, submission-ready version.
    * **Direct pushes to `main` are prohibited.** Protected branch.
    * Code is merged into `main` **only** from `develop` by the Project Manager (PM) before submission.

* **`develop` branch:**
    * Our primary integration branch. All completed task branches (features, fixes, etc.) merge here first.
    * Should always aim to be in a working state.
    * Task branches are created *from* `develop` and merged back *into* `develop` via Pull Requests.

* **Task Branches:**
    All work must be done in a dedicated task branch. The prefix indicates the type of work:

    * **Feature branches (`feature/<descriptive-name>`):**
        * For developing new features or functionalities.
        * Example: `feature/client-gui-form`, `feature/backend-flight-crud`

    * **Bugfix branches (`fix/<descriptive-name>`):**
        * For addressing and fixing bugs found in the `develop` branch or in existing features.
        * Example: `fix/client-id-uniqueness`, `fix/incorrect-login-redirect`

    * **Test branches (`test/<descriptive-name>`):**
        * For adding new tests (unit, integration, etc.) or refactoring existing tests. These branches should not contain production code changes.
        * Example: `test/add-user-service-tests`, `test/refactor-api-endpoint-tests`

    * **Chore branches (`chore/<descriptive-name>`):**
        * For housekeeping tasks, repository maintenance, updating build scripts, tooling configurations, dependency updates, or other operational tasks that don't directly modify `src` code related to features or bugs.
        * Example: `chore/update-linter-config`, `chore/organize-asset-folder`, `chore/bump-dependencies`

    * **Documentation branches (`docs/<descriptive-name>`):**
        * For making changes or additions purely to documentation (e.g., README, this `CONTRIBUTING.MD` file, user guides, API documentation).
        * Example: `docs/update-setup-guide`, `docs/add-api-usage-examples`

    * **How to create a task branch:**
        ```bash
        # Ensure you are on the develop branch and it's up-to-date
        git checkout develop
        git pull origin develop

        # Create and switch to your new task branch (replace <type> and <descriptive-name>)
        git checkout -b <type>/<descriptive-name>
        # Example: git checkout -b feature/new-user-profile
        # Example: git checkout -b chore/refactor-build-script
        ```

## 2. Commit Best Practices & Message Standards

To ensure our project's history is clear, understandable, and maintainable for years to come, we will strictly adhere to the following commit practices and message standards.

### 2.1. Guiding Principles for Commits

* **Atomicity:** Each commit **must stand alone as a single, complete, logical change.** It should represent one self-contained unit of work that someone might want to patch or revert in its entirety, never piece-wise. If a change could be useful in pieces, make separate commits.
* **Focus:** Avoid committing several unrelated changes in one go. This makes merging difficult and complicates bug tracking if an issue arises. Use `git gui` or similar tools if you need to commit selected parts or lines from your working changes.
* **Clarity:** The goal is a readable history that makes it easy to understand *why* a change was made. This is crucial for debugging (e.g., using `git bisect`) and for onboarding new team members.
* **No Extraneous Modifications:** A commit should not include unrelated whitespace changes, code style fixes in files not otherwise being modified by the commit's primary purpose, or other "noise."
    * **Reformatting code** without functional changes should generally be avoided. If such changes are absolutely necessary, they **must be in a separate commit** clearly documented as such (e.g., `style: Reformat user_interface module for PEP 8 compliance`). This prevents non-functional changes from obscuring the relevant parts of functional patches.
* **Coding Conventions:** All committed code should follow established coding conventions (e.g., PEP 8 for Python) closely.
* **Refactoring:**
    * Abstain from large, mixed refactorings where possible.
    * If refactoring is necessary, restrict it to its own commit (or series of commits) and document it clearly (e.g., `refactor: Extract user validation logic to new service`). Refactor commits should not change functionality.
    * Functionality changes (bug fixes or new features) should be in their own separate commits.

### 2.2. Commit Message Format

We will **strictly follow** the conventional commit message standard. This is a project requirement.

* **Format:**
    ```
    <type>: <subject>.

    [optional body: more detailed explanation, if needed, wrapped at 72 characters]

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

* **`<subject>` (First Line) rules:**
    * Written in the **imperative mood** (e.g., "Add login screen" NOT "Added login screen" or "Adds login screen"). Think of it as an instruction for what applying the commit will do.
    * Concise: Aim for **50 characters or less**, with a hard maximum of 72 characters.
    * **Must end with a period (`.`)**. Other punctuation like "..." should only be used if the summary line is intentionally incomplete and continues after a separator (rarely needed for us).
    * Do **not** start your commit message subject with a hash mark (`#`), as some git commands may dismiss these messages.

* **Commit Message Body (Optional but Recommended for Clarity):**
    * **Purpose:** Explain *why* the change is being made, not just *what* changed. Provide context that might be obscure to someone (or your future self!) reading it later.
    * **Motivation:** Include the motivation for the change and contrast its implementation with previous behavior if relevant.
    * **Details:** For more complex or significant changes, document relevant decisions, alternative solutions considered, side effects experienced, or other important considerations for anyone touching this code again. (Though detailed implementation logic is better suited for source code comments).
    * **Formatting:**
        * Separated from the subject line by a **blank line**.
        * Wrap the body text at **72 characters per line** (don't exceed 80). This improves readability in various Git tools.
        * Bullet points or numbered lists are acceptable and can improve clarity:
            ```
            * Typically a hyphen or asterisk is used for the bullet,
              preceded by a single space.
            * Use a hanging indent for multi-line bullet points.
            ```
    * **Bug Fixes:** If the commit fixes a bug, reference the issue number in the body or footer (e.g., `Fixes #123`).

* **Examples:**
    ```
    feat: Implement client data entry form.

    This form allows users to input new client information,
    including name, contact details, and address.
    Validations are in place for required fields.
    ```
    ```
    fix: Correct flight record deletion logic.

    Previously, deleting a flight did not properly update the
    associated passenger manifest. This commit ensures that
    passenger records are disassociated upon flight deletion.
    Closes #42.
    ```
    ```
    docs: Update README with GitHub workflow.
    ```
    ```
    test: Add unit tests for data_manager CRUD functions.
    ```
    ```
    chore: Update Python dependencies to latest versions.
    ```

### 2.3. Commit Frequency & Tidying Up

* **Commit Frequency:** Make small, logical, atomic commits. Each commit should represent a single, self-contained change. Work in consistent increments.
* **Clean History:** If your commit series includes "fix up" commits (e.g., "Fix typo.", "Fix test.", "Remove commented code."), please use `git rebase -i` (interactive rebase) to squash, fixup, or reword these commits into more meaningful ones **before submitting a pull request.** Aim for a readable history that clearly shows the progression of work.

## 3. Pull Requests (PRs)

* All `feature/*`, `fix/*`, `test/*`, `chore/*`, and `docs/*` branches **must be merged into `develop` via a Pull Request (PR)** on GitHub. Never merge directly into `develop` locally and push.
* **Creating a PR:**
    1.  Ensure your task branch is up-to-date with `develop` if necessary ( `git pull origin develop` into your task branch, resolve conflicts locally).
    2.  Push your completed task branch to GitHub: `git push -u origin <type>/your-task-name`.
    3.  Go to the project's GitHub repository page and click the "Compare & pull request" button for your branch.
    4.  Ensure the base branch is `develop` and the compare branch is your task branch.
    5.  Write a clear PR title (often reflects the main commit message or a summary of the task) and a comprehensive description. Summarize the changes, their purpose, how to test them, and link any related issues (e.g., "Closes #issue_number").
* **Review Process:**
    1.  Notify the team (e.g., in your group chat) that your PR is ready for review.
    2.  At least **one other team member** must review the PR. Assign a reviewer if needed.
    3.  **Reviewers should check for:**
        * Code clarity, correctness, and adherence to all contribution standards (including commit messages and branch naming).
        * Functionality (pull the branch locally and test thoroughly if possible).
        * Proper and sufficient tests for new code or changes (especially for `feature/*` and `fix/*` branches).
        * Potential bugs or edge cases.
        * Documentation updates if needed.
    4.  Provide feedback using GitHub's review tools (comments, suggestions, approval). Be constructive and specific.
* **Addressing Feedback:** The PR author **must** address all review comments/requests. Make additional commits to the same task branch (they will automatically update the PR). Strive to keep the discussion within the PR for traceability.
* **Merging a PR:**
    1.  Once the PR is approved by at least one reviewer and all discussions are resolved, it can be merged.
    2.  The **Project Manager (PM)** or a designated lead will perform the merge into `develop`.
    3.  Use **"Squash and merge"** (preferred for a clean `develop` history, combining all task branch commits into a single, well-crafted commit message on `develop`) or "Create a merge commit" if individual commits on the task branch are highly significant and need to be preserved.
    4.  **Delete the source branch** (task branch) after merging (GitHub provides a button for this).

## 4. General Workflow Summary

1.  **Sync `develop`:** Before starting any new work, always update your local `develop` branch:
    ```bash
    git checkout develop
    git pull origin develop
    ```
2.  **Create Task Branch:** Create your new task branch from the up-to-date `develop`, using the appropriate prefix:
    ```bash
    # Replace <type> with feature, fix, test, chore, or docs
    git checkout -b <type>/my-new-task-description
    ```
3.  **Develop & Commit:** Work on your task. Make frequent, small, atomic commits with proper, descriptive messages as outlined in Section 2. Test your changes locally.
4.  **Push & Create PR:** Once the task is complete and tested locally:
    ```bash
    # Replace <type> with feature, fix, test, chore, or docs
    git push -u origin <type>/my-new-task-description
    ```
    Go to GitHub and create a Pull Request targeting the `develop` branch.
5.  **Review & Merge:** Participate actively in the code review process. Address feedback promptly. Once approved, the PR will be merged by the PM/lead.
6.  **Clean Up:** After your PR is merged, you can delete your local task branch:
    ```bash
    # Replace <type> with feature, fix, test, chore, or docs
    git branch -d <type>/my-new-task-description
    ```
7.  **Repeat:** Sync `develop` again before starting the next task.

## 5. GitHub Issues

* Use GitHub Issues actively to track:
    * Bugs (`bug` label)
    * Feature requests/User stories (`feature` label)
    * Tasks (`task` label for `chore`, `test`, `docs` if not directly tied to a feature/bug)
    * Comments and short discussions for documentation reasons.
    * Long discussions should remain on MS Teams, but a summary or outcome can be documented in an issue.
* Use labels (`bug`, `feature`, `test`, `chore`, `docs`, `gui`, `backend`, `documentation`, `priority-high`, etc.) for organization and filtering.
* Reference issue numbers in commit messages (optional body/footer) or PR descriptions (e.g., `Closes #23`, `Fixes #45`, `Refs #45`) to automatically link them.

## 6. Git Author Configuration

Please ensure you have configured Git to use your correct name and email address for your commits. This helps in accurately tracking contributions. Use the same name and email on all machines you may push from.

* **To set your name and email globally (for all your Git repositories on your system):**
    ```bash
    git config --global user.name "Your Firstname Lastname"
    git config --global user.email "your_email@example.com"
    ```
* **To set it for just this project repository (run inside the project folder):**
    ```bash
    git config user.name "Your Firstname Lastname"
    git config user.email "your_email@example.com"
    ```
    You can also use `git gui` via `Edit` -> `Options…` to set these values.

---

Adhering to these standards will help us collaborate effectively, maintain a high-quality codebase, and deliver a successful project. Please ensure you understand and follow this workflow diligently.