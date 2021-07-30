# TC orna bot

[中文版](#tc-orna-bot-1)

A traditional chinese discord bot for [Orna：GPS RPG](https://playorna.com/)

## Features

-   show collaborative google sheet content
-   translate words between Chinese and English
-   auto-scan chinese equipments screenshot and return assessment
-   other useful commands

## Invite link

https://discordapp.com/api/oauth2/authorize?client_id=674503174551502857&permissions=2048&scope=bot

This bot only need Send Messages permission to work

Read permission will be required if that channel has restricted read permissions

## Usage

Only list important functions

For more usage please check help command

### Search command

```
~search <string>
```

Search content from google sheet, will show all content in the row

![](https://i.imgur.com/S5nHyVO.jpg)

```
~search index
```

Show all string available in the google sheet

![](https://i.imgur.com/pSic8Vv.jpg)

```
~search edit
```

Show google sheet url

### Translate command

```
~translate <string>
```

translate string between Chinese and English

String can be Chinese or English

Doesn't support fuzzy search, string need to match DB exactly

![](https://i.imgur.com/pQ5ySLp.jpg)

### Screenshot detection

```
~subscribe
```

Add this channel to the image auto-scan list

Channel list update every 10 second

```
~unsubscribe
```

Unlist this channel from auto-scan list

Now, you can post a screenshot on the channel that you made the bot subscribe to
![](https://i.imgur.com/lp6i33x.jpg)

This will return the embed message just like [Ornabot](https://orna.guide/gameplay?show=18) do

If anything goes wrong, the bot will return a [Ornabot](https://orna.guide/gameplay?show=18) %assess string, let you fix the string and post it again

\*\* To make %assess command work, You need [Ornabot](https://orna.guide/gameplay?show=18) in the server

![](https://i.imgur.com/P8z5NxG.jpg)

# TC orna bot

一個 [Orna：GPS RPG](https://playorna.com/) 的繁體中文 Discord bot

## 主要功能

-   顯示共同編輯的 google 試算表中的內容
-   遊戲中字詞的中翻英、英翻中
-   自動偵測遊戲裝備的截圖，並回傳 [Ornabot](https://orna.guide/gameplay?show=18) 的裝備查詢指令
-   其他有用的指令

## 邀請連結

https://discordapp.com/api/oauth2/authorize?client_id=674503174551502857&permissions=2048&scope=bot

本機器人只需要"傳送訊息"的權限

但在有設定讀取權限的頻道中，需要額外設定讀取訊息的權限才能正常運作

## 使用方法

只列出主要指令

其他指令請見機器人的 help 指令

### 搜尋指令

```
~search <搜尋詞彙>
```

搜尋 google 試算表中的內容，會顯示跟相符詞彙同一行的所有內容

![](https://i.imgur.com/S5nHyVO.jpg)

```
~search index
```

顯示 google 試算表中所有可搜尋的詞彙

![](https://i.imgur.com/pSic8Vv.jpg)

```
~search edit
```

顯示共同編輯的 google 試算表

### 翻譯指令

```
~translate <遊戲詞彙>
```

雙向翻譯中文/英文的詞彙

不支援模糊搜尋，必須與遊戲內的字一模一樣才能搜尋的到

![](https://i.imgur.com/pQ5ySLp.jpg)

### 截圖偵測

```
~subscribe
```

將此頻道增加到機器人自動偵測圖片的頻道列表中

頻道列表每 10 秒更新一次

```
~unsubscribe
```

將此頻道從機器人自動偵測圖片的頻道列表中移除

現在，你可以將遊戲中的物品截圖上傳到你剛剛讓機器人訂閱的頻道

![](https://i.imgur.com/lp6i33x.jpg)

機器人將會回傳跟 [Ornabot](https://orna.guide/gameplay?show=18) 一樣的訊息

若數值無法成功辨識，機器人會回傳 [Ornabot](https://orna.guide/gameplay?show=18) 的 %assess 指令字串，自行訂正後再將字串貼回頻道

要讓 %assess 指令生效，[Ornabot](https://orna.guide/gameplay?show=18) 必須要在同個伺服器內才能正常運作

![](https://i.imgur.com/P8z5NxG.jpg)
