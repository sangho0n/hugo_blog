---
title: "Hello"
layout: "about"
slug: "about"
---

# Welcome Visit! 👋

## About Me

In progress...

## About This Blog
This blog is built on the hugo framework and hugo-theme-stack theme. The primary language is Korean, but English is also supported.

Deployment is automatically done through GitHub Actions. The deployment process is as follows:

- Write posts in Korean
- git push -> execute workflow
- Check for changed or newly added `.md` files
- Translate those files into English (using OpenAI api; gpt3.5)
- Build with hugo
- Deploy the built files as a submodule
- Deploy to GitHub Pages from the submodule

If you are curious about more details, check out the [workflow](https://github.com/sangho0n/hugo_blog/blob/master/.github/workflows/main.yml)!

Although the title is dev-log, occasionally I will also post about hobbies and personal daily reflections in a diary-like format haha.