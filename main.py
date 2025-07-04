#.\.venv\Scripts\activate << lol i did that cuz i always forgot how to turn it on back then
import discord
import re
import requests
from datetime import timedelta, date, datetime, timezone
import os


botToken = os.getenv("DISCORD_BOT_TOKEN")
channelID = os.getenv("CHANNEL_ID") # discord channel id
trelloKey = os.getenv("TRELLO_API_KEY")
trelloToken = os.getenv("TRELLO_TOKEN")
messageDictionary = {}
#Test Board IDs
#6655ca29a8822d35e571646e
#6655ca29a8822d35e571646f
#6655ca29a8822d35e5716470



#Retrieves all cards in a list
def listCards(listID):
    url = f"https://api.trello.com/1/lists/{listID}/cards"
    query = {
        'key': trelloKey,
        'token': trelloToken
    }

    response = requests.request(
    "GET",
    url, 
    params=query
    )
    return response.json()



#Utilize Trello API to create the card
def addCard(offender, rank, length):
    url = "https://api.trello.com/1/cards"
    time = datetime.now(timezone.utc)
    dueDate = date.today() + timedelta(days=length)

    headers = {"Accept": "application/json"}
    query = {
    'name': offender,
    'desc': rank,
    'due':  '%sT%sZ' % (dueDate, time.strftime('%H:%M')),
    'key': trelloKey,
    'token': trelloToken
    }

    #Organizes which list the card goes under
    if length < 7:
        query.update({'idList': '65fe045e4aa4f53da57b021a'})
    if length >= 7 and length < 30:
        query.update({'idList': '65fe045e4aa4f53da57b021b'})
    if length >= 30:
        query.update({'idList': '65fe045e4aa4f53da57b021c'})

    response = requests.request(
    "POST",
    url,
    headers=headers,
    params=query
    )
    return



#Deletes cards. Calls listCards function to sort through all the carts in each list independently
def deleteCard(cardName):
    listIDs = ['65fe045e4aa4f53da57b021a', '65fe045e4aa4f53da57b021b', '65fe045e4aa4f53da57b021c']
    for listID in listIDs:
        cards = listCards(listID)
        for card in cards:
            if card['name'] == cardName:
                cardID = card['id']
                url = f"https://api.trello.com/1/cards/{cardID}"
                query = {
                'key': trelloKey,
                'token': trelloToken
                }

                response = requests.request(
                "DELETE",
                url, 
                params=query
                )
                return
                    


#Initial match to ensure that the format is being followed, if not, message is removed from dictionary.
def regEx(messageID):
    initialMatch = re.search(r'(\*\*Offender:\*\*)((.*))', messageDictionary[messageID])
    sentenceLength = re.search(r'(\*\*Class-E Sentence:\*\*)(\s*([1-9][0-9]?))', messageDictionary[messageID])
    rankPost = re.search(r'(\*\*Rank post-infraction:\*\*)((.*))', messageDictionary[messageID])

    if initialMatch:
        addCard(initialMatch.group(2).split()[0], rankPost.group(2), int(sentenceLength.group(2)))
        return

    else:
        messageDictionary.pop(messageID)
        return



#Class for Discord bot that waits for events.
class MyClient(discord.Client):
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == '⏰':
            messageID = reaction.message.id
            content = reaction.message.content
            messageDictionary.update({messageID: content})
            regEx(messageID)
            await reaction.message.add_reaction('✅') 
            return
        else:
            return
        
    async def on_reaction_remove(self, reaction, user):
        if reaction.emoji == '⏰':
            messageID = reaction.message.id
            if messageID in messageDictionary:
                cardName = messageDictionary.pop(messageID).split('\n')[0].split('**')[2].strip()
                deleteCard(cardName)
                await reaction.message.remove_reaction('✅', self.user) 
                return
        else:
            return

    async def on_message_delete(self, message):
        messageID = message.id
        userID = message.author.id
        if messageID in messageDictionary:
            cardName = messageDictionary.pop(messageID).split('\n')[0].split('**')[2].strip()
            deleteCard(cardName)
            return
        else:
            return
    

#Gives bot consent to read contents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Runs the client
client = MyClient(intents=intents)
client.run(botToken)