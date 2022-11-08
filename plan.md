- [Registration](#registration)
  - [Join](#join)
  - [Edit Join](#edit-join)
  - [Join Cancel](#join-cancel)
  - [Accept User](#accept-user)
  - [Deny User](#deny-user)
  - [Join Cancel User](#join-cancel-user)
  - [Join Cancel User (All)](#join-cancel-user-all)
- [Data viewing [Players Focus]](#data-viewing-players-focus)
  - [Show Union Members](#show-union-members)
  - [Show Union Members [Union]](#show-union-members-union)
  - [Show User](#show-user)
- [Data viewing [Nikke Focus]](#data-viewing-nikke-focus)
  - [Show Nikke](#show-nikke)
  - [Show Equipment](#show-equipment)
  - [Show Item](#show-item)

# Registration
## Join 

```
[+] /union-join
```

Allows the user to add themself for the waitlist of a union.  
Users will select which union they would like to join, then proceed to fill out a form.  
> If multiple entries have been found, a confirmation will be provided with a copy of the receipt of prior entries. If yes, adds another entry. If no, does not perform that entry.

Procedure
1. Post message for buttons to join
2. Each button shows a form to fill out
3. On confirm do below
   1. Try to add the user
      1. If full, report to both user and admin
      2. If unsuccessful, report to both user and admin
   2. Create receipt
   3. Try to send to DM, if not, channel

## Edit Join
```
[+] /union-join edit
```
Allows the user to select an entry and edit any information that can be editted.

Editable fields:
- Nikke ID
- Nikke Name
- Notes

Procedure
1. Post receipts or buttons for each entry
2. When clicked, show corresponding entry with form
   1. Follow similar to [Join](#join)

## Join Cancel
```
[+] /union-join cancel
```
Allows the user to remove themself from the waitlist of a union.  
If there are no entries, tell them.  
If there are multiple entries, the user will need to select the receipt corresponding to that entry.

## Accept User
**[ADMIN]**  
```
[+] /union-join accept @user
```
Allows an admin to accept a user, remove their entries and move them to the correct spreadsheet for the Union. The user is then notified of this through a DM or a server message.
> Admins should not interact with the spreadsheet to move users around. It will mainly be for observational purposes. Manually moving the user around will not provide a message for the user.

## Deny User
**[ADMIN]**  
```
[+] /union-join deny @user
```
Allows an admin to deny a user, remove their entry. The user is then notified of this through a DM or a server message.
> Admins should not interact with the spreadsheet to move users around. It will mainly be for observational purposes. Manually moving the user around will not provide a message for the user.

## Join Cancel User
**[ADMIN]**  
```
[+] /union-join cancel @user
```
Allows an admin to remove an entry of a corresponding user. Follows similar structure to [Join Cancel](#join-cancel)

## Join Cancel User (All)
**[Admin]**
```
[+] /union-join cancel-all @user
```
Similar to [Join Cancel user](#join-cancel-user-all) except removes all entries.

# Data viewing [Players Focus]
## Show Union Members
```
[+] /server-members
```
Shows all members in a list alongside their friendcode and which union they are in

## Show Union Members [Union]
```
[+] /union-members
```
Shows all members in a list alongside their friendcode.

## Show User
```
[+] /showuser @user
```
# Data viewing [Nikke Focus]
## Show Nikke
```
[+] /nikke name | alias
```
Presents an embed of the nikke

## Show Equipment
```
[+] /equipment name | alias
```
Presents an embed of the equipment

## Show Item
```
[+] /item name | alias
```
Presents an embed of the item
