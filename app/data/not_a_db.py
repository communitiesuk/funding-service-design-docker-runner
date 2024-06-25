COMPONENTS = {
    "reuse-alt-org-name-1": {
        "options": {"classes": "govuk-input"},
        "type": "TextField",
        "title": "Alternative name 1",
        "schema": {},
    },
    "reuse-alt-org-name-2": {
        "options": {"required": False, "classes": "govuk-input"},
        "type": "TextField",
        "title": "Alternative name 2",
        "schema": {},
    },
    "reuse-alt-org-name-3": {
        "options": {"required": False, "classes": "govuk-input"},
        "type": "TextField",
        "title": "Alternative name 3",
        "schema": {},
    },
    "reuse-organisation-name": {
        "options": {"hideTitle": False, "classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Organisation name",
        "hint": "This must match your registered legal organisation name",
        "schema": {},
    },
    "reuse-organisation-address": {
        "options": {},
        "type": "UkAddressField",
        "title": "Organisation address",
    },
    "reuse-english-region": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Which region of England do you work in?",
    },
    "reuse-charitable-objects": {
        "options": {"hideTitle": True, "maxWords": "500"},
        "type": "FreeTextField",
        "title": "What are your organisation's charitable objects?",
        "hint": "You can find this in your organisation's governing document.",
    },
    "ns-membership-organisations": {
        "options": {"hideTitle": True},
        "type": "RadiosField",
        "title": "Which membership organisations are you a member of?",
        "list": "list_ns_membership_organisations",
    },
    "reuse-organisation-main-purpose": {
        "options": {"hideTitle": True, "maxWords": "500"},
        "type": "FreeTextField",
        "title": "What is your organisation's main purpose?",
        "hint": "This is what the organisation was set up to achieve.",
    },
    "reuse_organisation_other_names_yes_no": {
        "options": {},
        "type": "YesNoField",
        "title": "Does your organisation use any other names?",
        "schema": {},
        "conditions": [
            {
                "name": "organisation_other_names_no",
                "value": "false",
                "operator": "is",
                "destination_page": "CONTINUE",
            },
            {
                "name": "organisation_other_names_yes",
                "value": "true",
                "operator": "is",
                "destination_page": "alternative-organisation-name",
            },
        ],
    },
    "reuse-organisation-website-social-media-links": {
        "options": {"columnTitles": ["Link", "Action"]},
        "type": "MultiInputField",
        "title": "Website and social media",
        "schema": {},
        "children": [
            {
                "name": "reuse-web-link",
                "options": {"classes": "govuk-!-width-full"},
                "type": "WebsiteField",
                "title": "Link",
                "hint": (
                    "<p>For example, your company's Facebook, Instagram or"
                    " Twitter accounts (if applicable)</p><p>You can add more"
                    " links on the next step</p>"
                ),
                "schema": {},
            }
        ],
    },
    "reuse-annual-turnover-23": {
        "options": {
            "prefix": "£",
            "hideTitle": True,
            "classes": "govuk-input--width-10",
        },
        "type": "NumberField",
        "title": "Annual turnover for 1 April 2022 to 31 March 2023",
        "hint": ('<label class="govuk-body" for="YauUjZ">1 April 2022 to 31 March' " 2023</label>"),
    },
    "reuse-annual-turnover-22": {
        "options": {
            "prefix": "£",
            "hideTitle": True,
            "classes": "govuk-input--width-10",
        },
        "type": "NumberField",
        "hint": ('<label class="govuk-body" for="zuCRBk">1 April 2021 to 31 March' " 2022</label>"),
        "title": "Annual turnover for 1 April 2021 to 31 March 2022",
    },
    "reuse-lead-contact-name": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Name of lead contact",
        "hint": ("They will receive all the information about this application."),
    },
    "reuse-lead-contact-job-title": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Lead contact job title",
    },
    "reuse-lead-contact-email": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "EmailAddressField",
        "title": "Lead contact email address",
    },
    "reuse-lead-contact-phone": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "TelephoneNumberField",
        "title": "Lead contact telephone number",
    },
    "reuse_is_lead_contact_same_as_auth_signatory": {
        "options": {},
        "type": "YesNoField",
        "title": ("Is the lead contact the same person as the authorised signatory?"),
        "hint": (
            '<p class="govuk-hint">An authorised signatory:<ul'
            ' class="govuk-list govuk-list--bullet govuk-hint"> <li>is allowed'
            " to act on behalf of the organisation</li> <li>will sign the"
            " grant funding agreement if your application is"
            " successful</li></ul></p>"
        ),
        "conditions": [
            {
                "name": "lead_contact_same_as_signatory_yes",
                "value": "true",
                "operator": "is",
                "destination_page": "CONTINUE",
            },
            {
                "name": "lead_contact_same_as_signatory_no",
                "value": "false",
                "operator": "is",
                "destination_page": "authorised-signatory-details",
            },
        ],
    },
    "reuse-alt-org-name-1": {
        "options": {"classes": "govuk-input"},
        "type": "TextField",
        "title": "Alternative name 1",
        "schema": {},
    },
    "reuse-alt-org-name-2": {
        "options": {"required": False, "classes": "govuk-input"},
        "type": "TextField",
        "title": "Alternative name 2",
        "schema": {},
    },
    "reuse-alt-org-name-3": {
        "options": {"required": False, "classes": "govuk-input"},
        "type": "TextField",
        "title": "Alternative name 3",
        "schema": {},
    },
    "auth-sig-intro": {
        "options": {},
        "type": "Html",
        "content": '<p class="govuk-hint">An authorised signatory:</p>\n<ul class="govuk-list govuk-list--bullet govuk-hint">\n            <li>is allowed to act on behalf of the organisation</li>\n            <li>will sign the grant funding agreement if your application is successful</li>\n          </ul>',
        "schema": {},
    },
    "auth-sig-full-name": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Authorised signatory full name",
        "schema": {},
    },
    "auth-sig-alt-name": {
        "options": {"required": False, "classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Alternative name",
        "schema": {},
    },
    "auth-sig-job-title": {
        "options": {"required": True, "classes": "govuk-!-width-full"},
        "type": "TextField",
        "title": "Authorised signatory job title",
        "schema": {},
    },
    "auth-sig-email": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "EmailAddressField",
        "title": "Authorised signatory email address",
        "schema": {},
    },
    "auth-sig-phone": {
        "options": {"classes": "govuk-!-width-full"},
        "type": "TelephoneNumberField",
        "title": "Authorised signatory telephone number",
        "schema": {},
    },
}
PAGES = [
    {
        "id": "organisation-single-name",
        "builder_display_name": "Single Organisation Name",
        "form_display_name": "Organisation Name",
        "component_names": [
            "reuse-organisation-name",
        ],
        "show_in_builder": True,
    },
    {
        "id": "organisation-name",
        "builder_display_name": "Organisation Name, with Alternatives",
        "form_display_name": "Organisation Name",
        "component_names": [
            "reuse-organisation-name",
            "reuse_organisation_other_names_yes_no",
        ],
        "show_in_builder": True,
    },
    {
        "id": "alternative-organisation-name",
        "form_display_name": "Alternative names of your organisation",
        "builder_display_name": "Alternative organisation names",
        "component_names": ["reuse-alt-org-name-1", "reuse-alt-org-name-2", "reuse-alt-org-name-3"],
        "show_in_builder": False,
    },
    {
        "id": "summary",
        "builder_display_name": "Summary",
        "form_display_name": "Check your answers",
        "component_names": [],
        "show_in_builder": False,
        "controller": "./pages/summary.js",
        "show_in_builder": False,
    },
    {
        "id": "alternative-organisation-name",
        "builder_display_name": "Alternative Organisation Names",
        "form_display_name": "Alternative names of your organisation",
        "component_names": [
            "reuse-alt-org-name-1",
            "reuse-alt-org-name-2",
            "reuse-alt-org-name-3",
        ],
        "show_in_builder": False,
    },
    {
        "id": "ns-org-name",
        "builder_display_name": "NSTF: Organisation Name",
        "form_display_name": "Organisation Name",
        "component_names": [
            "reuse-organisation-name",
            "reuse-organisation-address",
            "reuse-english-region",
        ],
    },
    {
        "id": "organisation-address",
        "builder_display_name": "Organisation Address",
        "form_display_name": "Registered organisation address",
        "component_names": ["reuse-organisation-address"],
    },
    {
        "id": "organisation-main-purpose",
        "builder_display_name": "Organisation Main Purpose",
        "form_display_name": "Organisation Main Purpose",
        "component_names": ["reuse-organisation-main-purpose"],
    },
    {
        "id": "organisation-web-links",
        "builder_display_name": "Organisation Web Links",
        "form_display_name": "Organisation Web Links",
        "component_names": ["reuse-organisation-website-social-media-links"],
        "controller": "RepeatingFieldPageController",
    },
    {
        "id": "annual-turnover",
        "builder_display_name": "Organisation Annual Turnover",
        "form_display_name": "Organisation Annual Turnover",
        "component_names": [
            "reuse-annual-turnover-22",
            "reuse-annual-turnover-23",
        ],
    },
    {
        "id": "ns-membership-organisations",
        "builder_display_name": "NSTF: Membership Organisaions",
        "form_display_name": "Organisation Membership",
        "component_names": ["ns-membership-organisations"],
    },
    {
        "id": "lead-contact-details-and-auth-signatory",
        "builder_display_name": "Lead Contact Details & Auth Signatory",
        "form_display_name": "Lead contact details",
        "component_names": [
            "reuse-lead-contact-name",
            "reuse-lead-contact-job-title",
            "reuse-lead-contact-email",
            "reuse-lead-contact-phone",
            "reuse_is_lead_contact_same_as_auth_signatory",
        ],
    },
    {
        "id": "authorised-signatory-details",
        "form_display_name": "Authorised signatory details",
        "builder_display_name": "Auth Signatory",
        "component_names": [
            "auth-sig-intro",
            "auth-sig-full-name",
            "auth-sig-alt-name",
            "auth-sig-job-title",
            "auth-sig-email",
            "auth-sig-phone",
        ],
    },
]

LISTS = {
    "list_ns_membership_organisations": {
        "type": "string",
        "items": [
            {"text": "Homeless Link", "value": "homeless-link"},
            {"text": "Housing Justice", "value": "housing-justice"},
            {"text": "Both", "value": "both"},
            {"text": "None", "value": "none"},
        ],
    }
}