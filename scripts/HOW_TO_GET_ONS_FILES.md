# Getting the ONS raw files

You do not need the old `Automation risk by occupation.xlsx` for the analysis. The cleaned risk scores are already in your repository at `data_work/risk.dta`, with 369 occupations and the same distribution the paper reports. Re-downloading the ONS workbook matters only so that the replication package builds from public sources end to end, which is worth having but is not blocking anything. What is blocking the five pending analyses is the ASHE Table 14 release files.

## The easy route, one command

Save `get_ashe_files.sh` (macOS) or `get_ashe_files.ps1` (Windows) somewhere convenient, such as your Desktop, then run it.

On macOS, open Terminal and type:

    cd ~/Desktop
    bash get_ashe_files.sh

On Windows, right-click `get_ashe_files.ps1` and choose "Run with PowerShell".

It downloads twelve files into a folder called `ashe_raw`, then makes `ashe_raw.zip`. Upload that zip to me. Total is roughly 80 MB and takes a couple of minutes. If a line prints FAILED, tell me which one and I will find the replacement link; the rest will still have downloaded.

## The manual route, if the script will not run

Everything sits on one ONS page. Open:

https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupation4digitsoc2010ashetable14

Scroll to the list of editions and download the **revised** edition for each of these years: 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023. Each is a zip of about 6 to 11 MB. Take the revised edition rather than the provisional one wherever both are offered, since revised is the final figure. Put all ten in one folder, zip it, and send it over.

For the automation-risk workbook, open:

https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/articles/whichoccupationsareathighestriskofbeingautomated/2019-03-25

and use the "Download the data" link under the **Occupation pay explorer** chart. That file pairs each occupation with its probability of automation. Download the one under the **Job automation chatbot** chart as well, since one of the two is the file you originally used and I can tell which by matching it against `risk.dta`.

## One thing to know before you run it

Your original build used whichever ASHE files you had on disk in 2025, and I cannot tell from the repository whether they were the provisional or the revised editions. The script takes revised for every year, which is the right choice for a published paper. Expect the rebuilt panel to differ slightly from `panel.dta` in a few cells. I will report every coefficient both ways so nothing moves silently, and the paper will state which edition it uses.

## What I will do once the files arrive

1. Rebuild the panel from the raw files, carrying mean pay, median pay, number of jobs, mean paid hours and the published percentiles.
2. Build the National Living Wage exposure share for 2015 from the percentiles and run the reviewer's triple-interaction design.
3. Run the employment-weighted estimates, the median-outcome estimates and the hourly-pay-excluding-overtime estimates.
4. Run employment and hours as outcomes, which is what answers the composition objection.
5. Settle why coverage falls after 2020 by reading the 2021 to 2023 files directly, and remove the CONFIRM marker in the draft.
6. Reconcile every number against the archived Stata output and report any that moves.
