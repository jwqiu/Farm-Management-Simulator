
# Design decisions

In this part, I want to talk about some features and functions I planned to make before developing this web application. For those features, I changed my mind during the development of this web application. I will talk more details, like my original plan and the reason why I changed it.

## Home page (Dashboard)

The assessment requirements ask me to make a home page which contains an image and introductory text (no practical function). I don't think this kind of home page is actually useful and practical. For example, whenever the user wants to access a practical function (like moving the mob, adding a new paddock), the user needs to access the home page first, then click and leave the home page. That doesn't make sense, that is why I want to make some differences to the home page. Instead of the farm management simulator, I want to make my web application more like a farm management system, so I tried to think from the actual user's (farmer's) perspective, what kind of home page they would like to have. I think the dashboard is a useful home page for farm management and operations. It helps farmers understand the overall operation of their farm. As far as I know, I think the farmer needs to move a mob or add a new paddock only in certain situations. They won't use this kind of function quite often, but they need to stay updated on their farm at all times. So, the dashboard is a more frequently used page compared to those add/move/edit functions. That's why I designed the home page as a dashboard.

There are two main features in my current dashboard. The first feature is to display key information and data metrics that help to keep the farmers updated about their farm, like the latest pasture level for each paddock and daily change rate, some growth and health metrics of the stocks. The second feature is a warning. I calculate and analyze potential issues from the farm's data to alert the farmer (although the data is quite limited). For example, how many stocks are underweight (need special attention), and when a certain paddock's pasture level is lower than 1500, I alert the farmer and suggest moving the mob immediately. I also inform the farmer about those paddocks where consumption is greater than growth, how many days until the pasture level will drop below 1500. That means the farmer needs to pay extra attention to it in the next few days. The warning feature helps the farmer find potential issues automatically and guides the farmer to take action (meaning the functions we made in this assessment, such as using the move mob function).

## Mobile user friendly interface

If you make the browser window smaller, you might find my web page looks good too, even on a phone-sized screen. Although the assessment requirements haven't asked for this kind of feature, it is an important skill to learn in this era. You know, people spend more time on phones rather than computers, and I think it's the same for the farmer.

## Stocks page

At first, I planned to use a long list to display all the stock information, but this would make the page really long, and it would take a lot of scrolling to see all the stock information. So, I made three tabs instead. Each tab displays stock information from one mob, which would make the page shorter. You can access stock information from different mobs with a single click rather than scrolling down for a while.

## Move_mob page

I planned to display only the currently available paddocks on the move_mob page when the users want to move a mob from one paddock to another (that is exactly what I did in my previous Python assessment), because it is meaningless to display those paddocks that are currently occupied; you cannot move a mob in them. However, after I completed the first version of the move_mob page, I found that if I didn't display those paddocks that are currently occupied, the users might be confused. I had this kind of confusion as well when I first tried the move mob function after I completed it. I was confused about why there was only one paddock option. Is there a bug in my code? (I forgot that only available paddocks would display on this page, even though I coded it.) From a logical perspective, it's okay not to display paddocks that are currently occupied, but from the user's perspective, they might expect to see all the paddocks on the page because they don't know the rules and logic behind it. This is a typical gap between the developer and the user. I think most users cannot immediately realize that other paddocks are currently occupied, so the developer didn't display them. So, I changed my move_mob function. I displayed all the paddocks on the move_mob page, but for those paddocks that are currently occupied, I made their buttons unclickable.

## Paddocks page

According to the assessment introduction, the regrowth might be affected once the pasture level drops below 1500, so I think the current pasture level is one of the key concerns for farmers. On top of that, if I were a farmer, I would also be concerned about those paddocks whose daily change rate is negative (meaning consumption is greater than growth), and how many days it will take for those paddocks' pasture levels to drop below 1500. I need to pay extra attention and make a plan to move mobs in advance to prevent the pasture level from dropping below 1500. So, I calculated and displayed the 'total_dm change per day' and 'falls below 1500 in x days' metrics for each paddock, although the assessment requirements have not asked for them.

I planned to provide only add & edit paddock functions on the paddocks list page at first, but finally, I added the move_mob function as well. This is because, when the users are browsing this page, the detailed information about the paddocks might make the user feel they should move mobs. For example, "Oh, this paddock's pasture level will drop below 1500 in 3 days, probably I should move the mob out of this paddock right now." I think this scenario will be quite common, and it makes sense to put a move_mob function on this page.

I also added a delete function on this page because this function can help delete some test data. It is more convenient to directly delete test data on this page rather than on MySQL Workbench. After I added this function, I realized that if those paddocks that are currently occupied by mobs can be deleted, that would be unreasonable. So, for those paddocks that are currently occupied, I made their delete buttons unclickable. By the way, the user will receive a hint when they hover over the delete button: "You can't delete this paddock because there is a mob in it so far," kind of notifying the user why this paddock cannot be deleted.

# Image sources

Paddock image. (n.d.). *Remtor*. https://remtor.com/en/paddocks/  
Cow image. (n.d.). *The Humane League*. https://thehumaneleague.org.uk/article/10-facts-about-cows-that-you-might-not-know

# Database questions

## Question 1: What SQL statement creates the mobs table and defines its fields/columns? (Copy and paste the relevant lines of SQL.)

CREATE TABLE mobs (
	id int NOT NULL AUTO_INCREMENT,
	name varchar(50) DEFAULT NULL,
	paddock_id int not null,
	PRIMARY KEY (id),
    UNIQUE INDEX paddock_idx (paddock_id),	-- Ensures that paddock_id is unique
	CONSTRAINT fk_paddock
		FOREIGN KEY (paddock_id)
		REFERENCES paddocks(id)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
);

## Question 2:Which lines of SQL script sets up the relationship between the mobs and paddocks tables?

   UNIQUE INDEX paddock_idx (paddock_id),	-- Ensures that paddock_id is unique
	CONSTRAINT fk_paddock
		FOREIGN KEY (paddock_id)
		REFERENCES paddocks(id)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION

## Question 3:The current FMS only works for one farm. Write SQL script to create a new table called farms, which includes a unique farm ID, the farm name, an optional short description and the owner’s name. The ID can be added automatically by the database. (Relationships to other tables not required.)

CREATE TABLE farms (
    id int NOT NULL AUTO_INCREMENT,
    farm_name varchar(100) NOT NULL,   
    description text NOT NULL,         
    owner_name varchar(100) NOT NULL,  
    PRIMARY KEY (id)
);

## Question 4:Write an SQL statement to add details for an example farm to your new farms table, which would be suitable to include in your web application for the users to add farms in a future version. (Type in actual values, don’t use %s markers.)

INSERT INTO farms(farm_name,description,owner_name)
VALUES('FarmofHope','a quite small farm that was set up by a young couple with a lovely kid','junwenqiu');

## Question 5: What changes would you need to make to other tables to incorporate the new farms table? (Describe the changes. SQL script not required.)

You didn't mention what the other tables are, so I assume 'other tables' means the paddocks, mobs, and stocks tables I used in this assessment,if i have the new farm tables, in order to link all these tables with the new farm tables, i need to add the farm_id as a foreign key to these talbe, so i can check which farm a certain stock/mob/stock is  in.

