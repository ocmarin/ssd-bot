# u/SSDBot
This is a Reddit bot that looks up SSDs posted within a subreddit and provides useful insight on the model found within the submission's title.

[u/SSDBot](https://www.reddit.com/u/SSDBot) will post comments under [r/BuildAPCSales](https://www.reddit.com/r/BuildAPCSales) submissions which are flaired as (any sort of) a SSD. The information the bot posts comes directly from [u/NewMaxx's](https://www.reddit.com/user/NewMaxx/) [SSDs spreadsheet.](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/edit#gid=0) Be sure to checkout his various [SSD guides & resources here!](https://www.reddit.com/r/NewMaxx/comments/dhvrdm/ssd_guides_resources/)

## Usage
The bot will automatically attempt to find an SSD mentioned in a submission. In order to increase the bot's ability to correctly identify an SSD, the following is recommended:
* Make certain the **brand name is in the title.**
* Contain the **model name** as *clearly as possible.*
* Have the brand/model **near the beginning of the title** (ie: immediately after the title).
* Do not include any **other** *model keywords* (eg: "Samsung 970 Evo" is better than "Samsung 970 Evo (not Plus)").
* If the bot **incorrectly identifies** the SSD, downvote the comment and it will record the issue automatically.

## Categories
Comments made by the bot will describe what *category of SSD* the given model falls under. This is explicitly written in the **first line of the comment.** This is a generalization about the usage the SSD; what it would perform best for and what type of customer the product is targetting.

### Category Types
[u/NewMaxx](https://www.reddit.com/user/NewMaxx/) (the creater of the [SSDs spreadsheet](https://docs.google.com/spreadsheets/d/1B27_j9NDPU3cNlj2HKcrfpJKHkOf-Oi1DbuuQva2gT4/edit#gid=0) this bot utilizes) describes the details of [what the categories mean in this post.](https://www.reddit.com/r/NewMaxx/comments/dhvrdm/ssd_guides_resources/) The following descriptions are *paraphrasings of those guides.*

#### Sata
* **Storage SATA**: Suitable for general data/games. Larger capacity, not the primary drive.
* **Light SATA**: Suitable for OS in light usage/secondary PCs. Smaller in capacity (so TLC based).
* **Budget SATA**: Suitable for OS use for primary PCs.
* **Performance SATA**: Suitable for anything.
#### NVMe
* **Budget NVMe**: Entry level SATA replacements, usually for mobile/HTPC usage.
* **Moderate NVMe**: Cheap alternative capable of any usage.
* **Consumer NVMe**: High performance drives for the best everyday experience.
* **Prosumer NVMe**: Specialized for content creation/workstation tasks. Generally some unique features/designs.
* **Prosumer/Consumer NVMe**: Flexible, all-arounders. The top drives.
