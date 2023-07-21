USE covid19;

DROP VIEW if exists health_symptoms;
CREATE VIEW health_symptoms AS 
    SELECT symptoms.symptomsID as symptomsID, 
        healthmanagement.userID as userID, 
        healthmanagement.recorddate as recorddate, 
        healthmanagement.timezone as timezone, 
        symptoms.temperature as temperature, 
        symptoms.jointpain as jointpain, 
        symptoms.washedoutfeeling as washedoutfeeling, 
        symptoms.headache as headache, 
        symptoms.sorethroat as sorethroat, 
        symptoms.breathless as breathless, 
        symptoms.coughsneezing as coughsneezing, 
        symptoms.nausea as nausea, 
        symptoms.abdominalpain as abdominalpain, 
        symptoms.tastedisorder as tastedisorder, 
        symptoms.olfactorydisorder as olfactorydisorder
    FROM healthmanagement 
    INNER JOIN symptoms
    ON healthmanagement.symptomsID = symptoms.symptomsID
;

DESC health_symptoms;