# Sub-skill: title lab

1. Write one title per family: number ("5 gaps..."), contrarian ("Your AI isn't the problem"), how-to ("How to..."), story ("I gave my juniors an AI assistant"), named problem ("The amnesia problem").
2. Cut any over about 60 characters or carrying a banned word.
3. Put all five in one file and run `rig-s1gate check substack.issue --file titles.md --subject "titles <post-id> sha256:<hash>" --json`. Keep the top two by score; if Jev is down, mark DEFERRED and pass all five to Mike.
4. Write the subtitle as the payoff sentence: "<what you get> so you can <outcome>".
5. Record the winner, runner-up and the Jev decision id in `package.md`.
