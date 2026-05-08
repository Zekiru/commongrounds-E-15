# Commissions Requests App

- [x] Pattern: Facade / Service Layer
- [x] app_name: commissions

## Models
- [x] CommissionType
    - [x] Name - max length is 255 character
    - [x] Description - text field
    - [x] Types should be sorted by name in ascending order

- [x] Commission
    - [x] Title - max length is 255 characters
    - [x] Description - text field 
    - [x] Type - foreign key to CommissionType, set to NULL when deleted
    - [x] Maker - foreign key to Profile, model deletion is cascaded
    - [x] People Required - should be whole number
    - [x] Status - character field with the following options:
        - Open (default)
        - Full
    - [x] Created On - datetime field, only gets set when the model is created
    - [x] Updated On - datetime field, always updates on last model update
    - [x] Commissions should be sorted by the date it was created, in ascending order

- [x] Job
    - [x] Commission - foreign key to Commission, model deletion is cascaded
    - [x] Role - max length is 255 characters
    - [x] Manpower Required - should be whole number
    - [x] Status - character field with the following options:
        - Open (default)
        - Full
    - [x] Jobs should be sorted by status (Open > Full), manpower required, in descending order, then role, in ascending order

- [x] JobApplication
    - [x] Job - foreign key to Job, model deletion is cascaded
    - [x] Applicant - foreign key to Profile, model deletion is cascaded
    - [x] Status - character field with the following options:
        - Pending (default)
        - Accepted
        - Rejected
    - [x] Applied On - datetime field, only gets set when the model is created
    - [x] Should be sorted by status (Pending first, then Accepted, then Rejected), then Applied On, in descending order

## Views
- [x] List View
    - [x] List ALL commissions in the system, regardless of poster and status. The commissions should follow this sorting schema:
        - Status (Open > Full > Completed > Discontinued)
        - Created On, most recent is shown first
    - [x] When logged in, there should be groups for the following commission entries, displayed first,  and removed from the All Commissions list:
        - Commissions the logged-in user has created
        - Commissions the logged-in user has applied to
    - [X] In this view, there should be a link that will lead to the creation of a commission.

- [x] Detail View
    - [x] This view should show the commission information and the list of Jobs needed for the Commission.
    - [x] A sum of manpower required, and open manpower (difference between sum of manpower and accepted signees) from the jobs should be shown.
    - [x] When logged in, the “Apply to Job” button to the Job should be open. This is essentially a JobApplication form, similar to the MerchStore Transaction form
    - [x] When the number of JobApplication entries with “Accepted” status is greater than or equal to the Job’s manpower required, the “Apply to Job” button should not be clickable.
    - [x] In this view, if the Commission's owner is the logged-in user, there should be an edit link that will lead to the update view.

- [x] Create View
    - [x] This view is only available if the Profile has the role “Commission Maker”.
    - [x] This should only be accessible to logged-in users.
    - [x] All fields should be available, including the corresponding Job objects, and the Maker field is set to the logged in user that is not editable.
    - [x] Status field should be a dropdown.

- [x] Update View
    - [x] This view is only available if the Profile has the role “Commission Maker”.
    - [x] This should only be accessible to logged-in users.
    - [x] It should allow updates of all fields except the Maker field.
    - [x] When all the commission’s jobs’ statuses are “Full”, the commission’s status should be set to “Full”.

## Advanced Requirements
- [x] Create a CommissionService class in *commissions/services.py*. Views must not contain business logic directly — all coordination between models must go through this service. It must implement the following methods:
    - [x] *create_commission(author, data, jobs_data)* — creates the Commission and all associated Job entries atomically
    - [x] *apply_to_job(applicant, job)* — creates a JobApplication, checking that the applicant has not already applied and that the job is not full
    - [x] *sync_commission_status(commission)* — checks all related Jobs and sets the commission status to "Full" if all jobs are full; called on every Commission update
    - [x] *get_commission_summary(commission)* — returns a dictionary with total_manpower and open_manpower computed from all related Jobs and their accepted applications

- [x] All four methods must be used in the appropriate views or signals.

- [x] *create_commission* must use *transaction.atomic()* to ensure the Commission and its Jobs are created together or not at all.

## Modifications
- [x] Modify Commission *status* Field Choices:
    - 0: Ongoing (default)
    - 1: Completed
    - 2: Discontinued
- [x] Create New Field - *jobs_status*:
    - 0: Open (default)
    - 1: Full
    - 2: Closed
- [x] *jobs_status* field cannot be modified by users.
- [x] If *status* != 0, then *recruitment_status* = 2.
    - Updated when *status* is modified
