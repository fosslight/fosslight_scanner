# Git Clone Authentication Guide


## Using SSH Key

1. **Generate SSH Key**:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "<user e-mail>@example.com"
//Follow the prompts to save the key in the default location.

2. **Add SSH Key to SSH Agent**:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_rsa

3. **Add SSH Key to SSH GitHub**:
    //Copy the SSH key to your clipboard
   ```bash
   cat ~/.ssh/id_rsa.pub
    //Go to GitHub, navigate to Settings > SSH and GPG keys, and click New SSH key. Paste the key and save.

4. **Clone the Repository Using SSH**:
   ```bash
   git clone git@github.com:chaeh03/fosslight_scanner.git


## USing Personal Access Token (PAT)

1. **Generate Personal Access Token(PAT)**:
    //Go to GitHub, navigate to Settings > Developer settings > Personal access tokens, and click Generate new token.
    //Select the necessary scopes and generate the token. Copy the generated token.

2. **Clone the Repository Using PAT**:
   ```bash
   git clone https://username:<your-token>@github.com/fosslight/fosslight_scanner.git
    //git clone https://username:<your-token>@github.com/fosslight/fosslight_scanner.git


## Save the File
    //Save the document with your changes (`Ctrl + S` or `Cmd + S`).


## Stage and Commit Changes

1. **Stage and Commit Changes**:
   //In the terminal, stage and commit your changes:
   ```bash
   git add gitauthentication.md
   git commit -m "Add guide for git clone authentication (#59)"

2. **Push to Remote Repository**:
    ```bash
   git push origin fix-issue-59


## Create a Pull Request

1. **Create a Pull Request on GitHub**:
    //Go to your forked repository's GitHub page.
    //Navigate to the "Pull Requests" tab and click "New Pull Request".
    //Select the fix-issue-59 branch and compare it with the base repository's 'main' or 'master' branch.
    //Write a title and description for your PR, mentioning the related issue number:

    //example: Fix: Add guide for git clone authentication

                    This PR adds a guide for setting up authentication when using git clone.

                    Related Issue: #59
    
    //Click "Create Pull Request" to submit your PR.
 
    
   

   