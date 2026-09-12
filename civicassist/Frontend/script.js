/* =====================================================
   CIVICASSIST AI - JAVASCRIPT
   ===================================================== */


/* =====================================================
   BACKEND CONNECTION (CivicAssist FastAPI backend)
   ===================================================== */

/*
   Change this if the backend runs somewhere other than
   the local FastAPI default (uvicorn app.main:app --reload
   from inside the Backend folder).
*/

const API_BASE_URL = "http://127.0.0.1:8001";


/*
   The login modal stores the language as a full display
   name ("English", "Hindi", ...). The backend expects a
   short language code, so we translate here.
*/

const LANGUAGE_NAME_TO_CODE = {
    English: "en",
    Hindi: "hi",
    Tamil: "ta",
    Telugu: "te",
    Kannada: "kn",
    Bengali: "bn",
    Marathi: "mr"
};


function getCurrentLanguageCode() {

    const savedLanguage =
        localStorage.getItem(
            "civicAssistLanguage"
        );


    return (
        LANGUAGE_NAME_TO_CODE[savedLanguage] ||
        "en"
    );

}


function getCurrentUserId() {

    try {

        const profileString =
            localStorage.getItem(
                "civicAssistProfile"
            );


        if (!profileString) {
            return null;
        }


        const profile =
            JSON.parse(profileString);


        return (
            profile.mobile ||
            profile.name ||
            null
        );

    } catch (error) {

        return null;

    }

}


/*
   Sends the citizen's message to the CivicAssist backend
   (/api/chat) and returns the parsed JSON response.

   Throws on network failure or a non-OK HTTP status so the
   caller can show a friendly error message instead of a
   silent failure.
*/

async function sendMessageToBackend(
    message,
    conversationId
) {

    const response =
        await fetch(
            `${API_BASE_URL}/api/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message,
                    user_id: getCurrentUserId(),
                    conversation_id: conversationId || null,
                    language: getCurrentLanguageCode()
                })
            }
        );


    if (!response.ok) {

        let detail = `Request failed with status ${response.status}.`;

        try {

            const errorBody =
                await response.json();

            if (errorBody && errorBody.detail) {

                detail = errorBody.detail;

            }

        } catch (parseError) {

            /* Response body was not JSON; keep default detail. */

        }

        throw new Error(detail);

    }


    return response.json();

}


/*
   Uploads a file the citizen attached in Smart Talk to the
   backend (/api/documents/upload) so it can be processed.
*/

async function uploadDocumentToBackend(file) {

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );


    const userId =
        getCurrentUserId();


    const url =
        userId
            ? `${API_BASE_URL}/api/documents/upload?user_id=${encodeURIComponent(userId)}`
            : `${API_BASE_URL}/api/documents/upload`;


    const response =
        await fetch(
            url,
            {
                method: "POST",
                body: formData
            }
        );


    if (!response.ok) {

        let detail = `Upload failed with status ${response.status}.`;

        try {

            const errorBody =
                await response.json();

            if (errorBody && errorBody.detail) {

                detail = errorBody.detail;

            }

        } catch (parseError) {

            /* Response body was not JSON; keep default detail. */

        }

        throw new Error(detail);

    }


    return response.json();

}


/* ================= SCHEME DATA ================= */

const schemes = [

    /* EDUCATION */

    {
        name: "Samagra Shiksha",
        category: "Education",
        description:
            "Government support for school education and learning.",
        details:
            "Samagra Shiksha supports school education through an integrated approach covering pre-school, primary, secondary and higher secondary education.",
        documents: [
            "Aadhaar Card",
            "Student identity proof",
            "School-related documents"
        ],
        charges:
            "No direct application charge through the official government scheme process.",
        where:
            "Relevant government education department, school authorities or official government portal."
    },

    {
        name: "PM POSHAN",
        category: "Education",
        description:
            "Nutritional support for eligible school students.",
        details:
            "PM POSHAN provides nutritional support to children in eligible schools as part of the government school education system.",
        documents: [
            "Student records",
            "School records",
            "Identity documentation where applicable"
        ],
        charges:
            "No direct application charge.",
        where:
            "Participating government and government-aided schools."
    },

    {
        name:
            "National Means-cum-Merit Scholarship Scheme (NMMSS)",
        category: "Education",
        description:
            "Scholarship support for eligible meritorious students.",
        details:
            "NMMSS provides financial assistance to eligible students to encourage them to continue secondary education.",
        documents: [
            "Student identity proof",
            "Academic records",
            "Income-related documents where required"
        ],
        charges:
            "No direct application charge under the scheme.",
        where:
            "Official scholarship portal and concerned educational authorities."
    },


    /* EMPLOYMENT */

    {
        name: "MGNREGA",
        category: "Employment",
        description:
            "Employment support through guaranteed rural wage employment.",
        details:
            "MGNREGA provides guaranteed wage employment opportunities in rural areas for eligible households.",
        documents: [
            "Aadhaar Card",
            "Job card or employment registration documents",
            "Bank account information"
        ],
        charges:
            "No application charge.",
        where:
            "Gram Panchayat or authorised government employment system."
    },

    {
        name:
            "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
        category: "Employment",
        description:
            "Skill development and training support.",
        details:
            "PMKVY supports skill development and vocational training for eligible candidates.",
        documents: [
            "Aadhaar Card",
            "Educational documents",
            "Mobile number"
        ],
        charges:
            "Training support is provided under participating programmes; exact conditions may vary.",
        where:
            "Authorised training centres and official skill-development channels."
    },

    {
        name: "National Career Service (NCS)",
        category: "Employment",
        description:
            "Employment and career-related information and services.",
        details:
            "NCS connects job seekers and employers and provides career-related information and services.",
        documents: [
            "Aadhaar or other identity proof",
            "Educational details",
            "Employment profile information"
        ],
        charges:
            "Basic NCS services are provided without an application fee.",
        where:
            "Official National Career Service portal and affiliated centres."
    },

    /* DISABILITY */
    {
        name: "ADIP",
        category: "Disability",
        description:
            "Assistive Devices & Rehabilitation",
        details:
            "The ADIP schemes provides devices to improve their independance and functioning.",
        documents: [
            "UDID card",
            "Aadhaar or other identity proof",
            "Income certificate"
        ],
        charges:
            "No application fee.",
        where:
            "Official ARJUN-ADIP portal."
    },

     {
        name: "Unique Disability ID (UDID)",
        category: "Disability",
        description:
            "Disability Certificate.",
        details:
            "The UDID provides the certificate to disabled persons.",
        documents: [
            "Aadhaar or other identity proof",
            "Address proof",
            "Medical/Disability related document"
        ],
        charges:
            "No application fee.",
        where:
            "Official UDID portal."
    },

     {
        name: "Disability Pension",
        category: "Disability",
        description:
            "The pension given to the disabled persons.",
        details:
            "The financial support for disabled persons.",
        documents: [
            "UDID card",
            "Family/Rattion card",
            "Bank account details"
        ],
        charges:
            "No applicable fee.",
        where:
            "Disctrrict Differently Abled Welfare Officer(DDAWO)."
    },


    /* HEALTHCARE */

    {
        name:
            "Ayushman Bharat – PM-JAY",
        category: "Healthcare",
        description:
            "Health coverage support for eligible families.",
        details:
            "Ayushman Bharat PM-JAY provides health coverage support to eligible beneficiary families.",
        documents: [
            "Aadhaar Card or accepted identity proof",
            "Beneficiary identification documents",
            "Supporting family details where required"
        ],
        charges:
            "No beneficiary application fee.",
        where:
            "Empanelled hospitals, authorised centres and official government channels."
    },

    {
        name:
            "Ayushman Arogya Mandirs",
        category: "Healthcare",
        description:
            "Accessible primary healthcare services.",
        details:
            "Ayushman Arogya Mandirs provide a range of primary healthcare services closer to communities.",
        documents: [
            "Identity proof where applicable",
            "Health-related records if available"
        ],
        charges:
            "Services depend on the applicable public health programme.",
        where:
            "Ayushman Arogya Mandirs and designated public healthcare facilities."
    },

    {
        name:
            "Jan Aushadhi Scheme (PMBJP)",
        category: "Healthcare",
        description:
            "Affordable medicines through Jan Aushadhi centres.",
        details:
            "The Jan Aushadhi scheme promotes availability of quality generic medicines at affordable prices through designated centres.",
        documents: [
            "Prescription where required",
            "Identity information where required"
        ],
        charges:
            "Medicine prices vary by product; there is no general scheme registration fee for purchasing medicines.",
        where:
            "Authorised Jan Aushadhi Kendras."
    },


    /* HOME */

    {
        name:
            "Pradhan Mantri Awas Yojana – Gramin (PMAY-G)",
        category: "Home",
        description:
            "Housing support for eligible rural households.",
        details:
            "PMAY-G supports eligible rural households in obtaining assistance for permanent housing.",
        documents: [
            "Aadhaar Card",
            "Proof of residence",
            "Income or beneficiary-related documents where applicable"
        ],
        charges:
            "No application fee under the government scheme.",
        where:
            "Gram Panchayat and concerned rural development authorities."
    },

    {
        name:
            "Pradhan Mantri Awas Yojana – Urban (PMAY-U)",
        category: "Home",
        description:
            "Housing support for eligible urban beneficiaries.",
        details:
            "PMAY-U supports eligible urban households through applicable housing assistance mechanisms.",
        documents: [
            "Aadhaar Card",
            "Address proof",
            "Income-related documents",
            "Other scheme-specific documents"
        ],
        charges:
            "Application conditions and charges depend on the applicable component and authority.",
        where:
            "Urban local body, designated authority or official government portal."
    },

    {
        name:
            "PM SVANidhi",
        category: "Home",
        description:
            "Support for eligible street vendors.",
        details:
            "PM SVANidhi supports eligible street vendors with access to working-capital assistance.",
        documents: [
            "Identity proof",
            "Street-vendor related identification",
            "Bank details"
        ],
        charges:
            "No standard application fee.",
        where:
            "Urban local bodies, authorised financial institutions and official PM SVANidhi channels."
    },


    /* FARMER */

    {
        name: "PM-KISAN",
        category: "Farmer",
        description:
            "Income support for eligible farmer families.",
        details:
            "PM-KISAN provides income support to eligible farmer families subject to scheme conditions.",
        documents: [
            "Aadhaar Card",
            "Land-related records",
            "Bank account information"
        ],
        charges:
            "No application fee.",
        where:
            "Official PM-KISAN portal, state government agriculture system or authorised service centre."
    },

    {
        name:
            "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        category: "Farmer",
        description:
            "Crop insurance support for eligible farmers.",
        details:
            "PMFBY provides crop insurance support against specified crop-related risks for eligible farmers.",
        documents: [
            "Aadhaar Card",
            "Land records",
            "Bank details",
            "Crop or cultivation details"
        ],
        charges:
            "Farmer premium depends on applicable crop and scheme rules.",
        where:
            "Authorised banks, insurance channels and government agriculture portals."
    },

    {
        name:
            "Kisan Credit Card (KCC)",
        category: "Farmer",
        description:
            "Credit support for eligible farmers.",
        details:
            "KCC provides access to agricultural credit facilities for eligible farmers.",
        documents: [
            "Aadhaar or identity proof",
            "Land records",
            "Address proof",
            "Bank-related documents"
        ],
        charges:
            "Terms and applicable charges depend on the lending institution and applicable rules.",
        where:
            "Participating banks and authorised financial institutions."
    }

];


/* ================= DOM ELEMENTS ================= */

const loginBtn =
    document.getElementById("loginBtn");

const loginModal =
    document.getElementById("loginModal");

const closeLoginModal =
    document.getElementById("closeLoginModal");

const loginForm =
    document.getElementById("loginForm");

const mobileNumber =
    document.getElementById("mobileNumber");

const userLanguage =
    document.getElementById("userLanguage");

const loginSuccessMessage =
    document.getElementById("loginSuccessMessage");

const successMessageText =
    document.getElementById("successMessageText");

const closeSuccessMessage =
    document.getElementById("closeSuccessMessage");

const logoutOverlay =
    document.getElementById("logoutOverlay");

const logoutCancel =
    document.getElementById("logoutCancel");

const logoutConfirm =
    document.getElementById("logoutConfirm");

const schemeSearchForm =
    document.getElementById("schemeSearchForm");

const userNeed =
    document.getElementById("userNeed");

const schemeList =
    document.getElementById("schemeList");

const findSchemesBtn =
    document.getElementById("findSchemesBtn");

const featuresGrid =
    document.getElementById("featuresGrid");

const featureDetails =
    document.getElementById("featureDetails");

const selectedFeatureTitle =
    document.getElementById("selectedFeatureTitle");

const selectedSchemeName =
    document.getElementById("selectedSchemeName");

const featureSchemeList =
    document.getElementById("featureSchemeList");

const featureBackBtn =
    document.getElementById("featureBackBtn");


/* ================= SCHEME DETAILS ================= */

const schemeDetailsView =
    document.getElementById(
        "schemeDetailsView"
    );

const schemeSelectedName =
    document.getElementById(
        "schemeSelectedName"
    );

const schemeSelectedShortDescription =
    document.getElementById(
        "schemeSelectedShortDescription"
    );

const schemeBackButton =
    document.getElementById(
        "schemeBackButton"
    );

const schemeInformationPanel =
    document.getElementById(
        "schemeInformationPanel"
    );

const schemeEligibilityPanel =
    document.getElementById(
        "schemeEligibilityPanel"
    );

const schemeFullDescription =
    document.getElementById(
        "schemeFullDescription"
    );

const schemeDocuments =
    document.getElementById(
        "schemeDocuments"
    );

const schemeCharges =
    document.getElementById(
        "schemeCharges"
    );

const schemeWhereToApply =
    document.getElementById(
        "schemeWhereToApply"
    );

const mainEligibilityTestBtn =
    document.getElementById(
        "mainEligibilityTestBtn"
    );

const eligibilitySchemeTitle =
    document.getElementById(
        "eligibilitySchemeTitle"
    );

const eligibilityForm =
    document.getElementById(
        "eligibilityForm"
    );

const eligibilityAge =
    document.getElementById("eligibilityAge");

const eligibilityState =
    document.getElementById("eligibilityState");

const eligibilityOccupation =
    document.getElementById("eligibilityOccupation");

const eligibilityIncome =
    document.getElementById("eligibilityIncome");

const eligibilityCategory =
    document.getElementById("eligibilityCategory");

const eligibilityDocuments =
    document.getElementById("eligibilityDocuments");

const eligibilityClearBtn =
    document.getElementById(
        "eligibilityClearBtn"
    );

const eligibilityResultMessage =
    document.getElementById(
        "eligibilityResultMessage"
    );


/* ================= SMART TALK ================= */

const smartTalkPage =
    document.getElementById(
        "smartTalkPage"
    );

const smartTalkExitBtn =
    document.getElementById(
        "smartTalkExitBtn"
    );

const smartTalkForm =
    document.getElementById(
        "smartTalkForm"
    );

const smartTalkInput =
    document.getElementById(
        "smartTalkInput"
    );

const chatMessages =
    document.getElementById(
        "chatMessages"
    );

const smartTalkSuggestions =
    document.querySelectorAll(
        ".smart-talk-suggestion"
    );

const smartTalkUploadBtn =
    document.getElementById(
        "smartTalkUploadBtn"
    );

const smartTalkFileInput =
    document.getElementById(
        "smartTalkFileInput"
    );

const smartTalkLanguageBtn =
    document.getElementById(
        "smartTalkLanguageBtn"
    );

const smartTalkLanguageOverlay =
    document.getElementById(
        "smartTalkLanguageOverlay"
    );

const smartTalkLanguageCloseBtn =
    document.getElementById(
        "smartTalkLanguageCloseBtn"
    );

const smartTalkLanguageOptions =
    document.querySelectorAll(
        ".smart-talk-language-option"
    );

const smartTalkHistoryList =
    document.getElementById(
        "smartTalkHistoryList"
    );

const smartTalkNewChatBtn =
    document.getElementById(
        "smartTalkNewChatBtn"
    );


/* ================= STATE ================= */

let selectedScheme = null;

let eligibilityResultTimeout = null;

let smartTalkOpen = false;


/* ================= LOGIN STATE ================= */

function isUserLoggedIn() {

    return Boolean(
        localStorage.getItem(
            "civicAssistProfile"
        )
    );

}


function updateLoginButton() {

    if (!loginBtn) {
        return;
    }


    loginBtn.textContent =
        isUserLoggedIn()
            ? "Logout"
            : "Login";

}


/* ================= LOGIN MODAL ================= */

function openLoginModal() {

    if (!loginModal) {
        return;
    }


    /* Load previously selected language */

    const savedLanguage =
        localStorage.getItem(
            "civicAssistLanguage"
        );


    if (
        savedLanguage &&
        userLanguage
    ) {

        userLanguage.value =
            savedLanguage;

    }


    loginModal.classList.add(
        "show"
    );


    setTimeout(
        function () {

            const nameInput =
                document.getElementById(
                    "userName"
                );


            if (nameInput) {

                nameInput.focus();

            }

        },
        100
    );

}


function closeLoginModalFunction() {

    if (!loginModal) {
        return;
    }


    loginModal.classList.remove(
        "show"
    );

}


if (closeLoginModal) {

    closeLoginModal.addEventListener(
        "click",
        closeLoginModalFunction
    );

}


if (loginModal) {

    loginModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                loginModal
            ) {

                closeLoginModalFunction();

            }

        }
    );

}


/* ================= MOBILE VALIDATION ================= */

if (mobileNumber) {

    mobileNumber.addEventListener(
        "input",
        function () {

            this.value =
                this.value
                    .replace(/\D/g, "")
                    .slice(0, 10);

        }
    );

}


/* ================= LOGIN FORM ================= */

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            const name =
                document
                    .getElementById(
                        "userName"
                    )
                    .value
                    .trim();


            const state =
                document
                    .getElementById(
                        "userState"
                    )
                    .value;


            const language =
                userLanguage
                    ? userLanguage.value
                    : "";


            const mobile =
                mobileNumber
                    .value
                    .trim();


            if (
                name.length < 2
            ) {

                alert(
                    "Please enter a valid name."
                );

                return;

            }


            if (!state) {

                alert(
                    "Please select your state."
                );

                return;

            }


            if (!language) {

                alert(
                    "Please select your preferred language."
                );

                return;

            }


            if (
                !/^\d{10}$/.test(
                    mobile
                )
            ) {

                alert(
                    "Please enter a valid 10-digit mobile number."
                );

                return;

            }


            const profile = {

                name: name,

                state: state,

                language: language,

                mobile: mobile

            };


            localStorage.setItem(
                "civicAssistProfile",
                JSON.stringify(profile)
            );


            /* Save language for Smart Talk */

            localStorage.setItem(
                "civicAssistLanguage",
                language
            );


            updateLoginButton();

            closeLoginModalFunction();

            showLoginSuccess(
                name
            );

        }
    );

}


/* ================= LOGIN SUCCESS ================= */

function showLoginSuccess(
    name
) {

    if (!loginSuccessMessage) {
        return;
    }


    successMessageText.textContent =
        `Welcome, ${name}! Your CivicAssist profile is ready.`;


    loginSuccessMessage.classList.add(
        "show"
    );


    clearTimeout(
        window.loginSuccessTimeout
    );


    window.loginSuccessTimeout =
        setTimeout(
            function () {

                hideLoginSuccess();

            },
            4500
        );

}


function hideLoginSuccess() {

    if (!loginSuccessMessage) {
        return;
    }


    loginSuccessMessage.classList.remove(
        "show"
    );

}


if (closeSuccessMessage) {

    closeSuccessMessage.addEventListener(
        "click",
        hideLoginSuccess
    );

}


/* ================= LOGOUT ================= */

function openLogoutDialog() {

    if (!logoutOverlay) {
        return;
    }


    logoutOverlay.classList.add(
        "show"
    );

}


function closeLogoutDialog() {

    if (!logoutOverlay) {
        return;
    }


    logoutOverlay.classList.remove(
        "show"
    );

}


function showLogoutSuccess() {

    if (!loginSuccessMessage) {
        return;
    }


    successMessageText.textContent =
        "You have been safely logged out of CivicAssist.";


    loginSuccessMessage.classList.add(
        "show"
    );


    clearTimeout(
        window.loginSuccessTimeout
    );


    window.loginSuccessTimeout =
        setTimeout(
            function () {

                hideLoginSuccess();

            },
            4500
        );

}


if (loginBtn) {

    loginBtn.addEventListener(
        "click",
        function () {

            if (
                isUserLoggedIn()
            ) {

                openLogoutDialog();

            } else {

                openLoginModal();

            }

        }
    );

}


if (logoutCancel) {

    logoutCancel.addEventListener(
        "click",
        closeLogoutDialog
    );

}


if (logoutConfirm) {

    logoutConfirm.addEventListener(
        "click",
        function () {

            localStorage.removeItem(
                "civicAssistProfile"
            );

            localStorage.removeItem(
                "civicAssistLanguage"
            );


            updateLoginButton();

            closeLogoutDialog();

            showLogoutSuccess();

        }
    );

}


if (logoutOverlay) {

    logoutOverlay.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                logoutOverlay
            ) {

                closeLogoutDialog();

            }

        }
    );

}


/* ================= FEATURE CARD ACTIONS ================= */

const originalFeatureCards =
    featuresGrid
        ? Array.from(
            featuresGrid.querySelectorAll(
                ".feature-card"
            )
        )
        : [];


function openFeatureCard(
    card
) {

    if (
        !featuresGrid ||
        !featureDetails ||
        !card
    ) {

        return;

    }


    const category =
        card.dataset.category ||
        card
            .querySelector("h3")
            ?.textContent
            .trim();


    const categorySchemes =
        schemes.filter(
            scheme =>
                scheme.category ===
                category
        );


    featuresGrid.prepend(
        card
    );


    featuresGrid.appendChild(
        featureDetails
    );


    originalFeatureCards.forEach(
        featureCard => {

            featureCard.classList.toggle(
                "feature-card-hidden",
                featureCard !== card
            );

        }
    );


    featuresGrid.classList.add(
        "feature-detail-active"
    );


    selectedFeatureTitle.textContent =
        category;


    featureSchemeList.innerHTML =
        categorySchemes
            .map(
                scheme => `
                    <div class="feature-scheme-item">
                        ${scheme.name}
                    </div>
                `
            )
            .join("");


    selectedSchemeName.textContent =
        categorySchemes.length
            ? "Available Government Schemes"
            : "No scheme added yet";


    featureDetails.classList.add(
        "show"
    );


    featureDetails.setAttribute(
        "aria-hidden",
        "false"
    );


    card.classList.add(
        "feature-card-selected"
    );


    featureDetails.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });

}


function closeFeatureCard() {

    if (
        !featuresGrid ||
        !featureDetails
    ) {

        return;

    }


    originalFeatureCards.forEach(
        featureCard =>
            featuresGrid.appendChild(
                featureCard
            )
    );


    featuresGrid.appendChild(
        featureDetails
    );


    originalFeatureCards.forEach(
        featureCard => {

            featureCard.classList.remove(
                "feature-card-hidden",
                "feature-card-selected"
            );

        }
    );


    featuresGrid.classList.remove(
        "feature-detail-active"
    );


    featureDetails.classList.remove(
        "show"
    );


    featureDetails.setAttribute(
        "aria-hidden",
        "true"
    );

}


if (featuresGrid) {

    featuresGrid
        .querySelectorAll(
            ".feature-card"
        )
        .forEach(
            card => {

                const button =
                    card.querySelector(
                        ".feature-btn"
                    );


                if (button) {

                    button.addEventListener(
                        "click",
                        function () {

                            if (
                                card.classList.contains(
                                    "feature-card-selected"
                                )
                            ) {

                                closeFeatureCard();

                            } else {

                                openFeatureCard(
                                    card
                                );

                            }

                        }
                    );

                }

            }
        );

}


if (featureBackBtn) {

    featureBackBtn.addEventListener(
        "click",
        closeFeatureCard
    );

}


/* ================= SEARCH ================= */

if (schemeSearchForm) {

    schemeSearchForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            if (
                !isUserLoggedIn()
            ) {

                openLoginModal();

                return;

            }


            const query =
                userNeed.value
                    .trim()
                    .toLowerCase();


            if (!query) {

                schemeList.innerHTML = `
                    <div class="scheme-result">

                        <h3>
                            Tell us what you need
                        </h3>

                        <p>
                            Enter something like education,
                            healthcare, employment, scholarship,
                            home, or farmer.
                        </p>

                    </div>
                `;

                return;

            }


            let category = "";


            if (
                query.includes("health") ||
                query.includes("medical") 
            ) {

                category = "Healthcare";

            } else if (
                query.includes("education") ||
                query.includes("scholarship") ||
                query.includes("student")
            ) {

                category = "Education";

            } else if (
                query.includes("job") ||
                query.includes("employment") ||
                query.includes("career")
            ) {

                category = "Employment";

            }else if (
    		query.includes("disability") ||
    		query.includes("disabled") ||
    		query.includes("udid") ||
    		query.includes("adip")
	    ) {
    		category = "Disability";


		} else if (
                query.includes("home") ||
                query.includes("house") ||
                query.includes("housing")
            ) {

                category = "Home";

            } else if (
                query.includes("farmer") ||
                query.includes("farming") ||
                query.includes("agriculture")
            ) {

                category = "Farmer";

            }


            const results =
                category
                    ? schemes.filter(
                        scheme =>
                            scheme.category ===
                            category
                    )
                    : schemes;


            displaySchemes(
                results
            );

        }
    );

}


/* ================= DISPLAY SCHEMES ================= */

function displaySchemes(
    results
) {

    if (!schemeList) {
        return;
    }


    if (!results.length) {

        schemeList.innerHTML = `
            <div class="scheme-result">

                <h3>
                    No schemes found
                </h3>

                <p>
                    Try searching for another
                    type of government support.
                </p>

            </div>
        `;

        return;

    }


    schemeList.innerHTML =
        results
            .map(
                scheme => `
                    <div class="scheme-result">

                        <h3>
                            ${scheme.name}
                        </h3>

                        <p>
                            ${scheme.description}
                        </p>

                        <button
                            type="button"
                            class="scheme-view-details"
                            data-scheme-name="${encodeURIComponent(
                                scheme.name
                            )}"
                        >

                            <span>
                                View Details
                            </span>

                            <span>
                                →
                            </span>

                        </button>

                    </div>
                `
            )
            .join("");


    attachSchemeDetailsButtons();

}


/* ================= SCHEME DETAILS BUTTONS ================= */

function attachSchemeDetailsButtons() {

    if (!schemeList) {
        return;
    }


    schemeList
        .querySelectorAll(
            ".scheme-view-details"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function () {

                        const schemeName =
                            decodeURIComponent(
                                this.dataset.schemeName
                            );


                        const scheme =
                            schemes.find(
                                item =>
                                    item.name ===
                                    schemeName
                            );


                        if (!scheme) {
                            return;
                        }


                        openSchemeDetails(
                            scheme
                        );

                    }
                );

            }
        );

}


/* ================= OPEN SCHEME DETAILS ================= */

function openSchemeDetails(
    scheme
) {

    if (!schemeDetailsView) {
        return;
    }


    selectedScheme = {
        ...scheme,
        id: scheme.id || scheme.name
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "")
    };


    schemeSelectedName.textContent =
        scheme.name;


    schemeSelectedShortDescription.textContent =
        scheme.description;


    schemeFullDescription.textContent =
        scheme.details;


    schemeDocuments.innerHTML =
        scheme.documents
            .map(
                documentName =>
                    `<li>${documentName}</li>`
            )
            .join("");


    schemeCharges.textContent =
        scheme.charges;


    schemeWhereToApply.textContent =
        scheme.where;


    eligibilitySchemeTitle.textContent =
        scheme.name;


    schemeList.style.display =
        "none";


    schemeDetailsView.classList.add(
        "show"
    );


    schemeDetailsView.setAttribute(
        "aria-hidden",
        "false"
    );


    schemeInformationPanel.style.display =
        "block";


    schemeEligibilityPanel.classList.remove(
        "show"
    );


    schemeEligibilityPanel.setAttribute(
        "aria-hidden",
        "true"
    );


    restoreEligibilityButton();


    clearEligibilityForm();


    schemeDetailsView.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* ================= CLOSE SCHEME DETAILS ================= */

function closeSchemeDetails() {

    if (!schemeDetailsView) {
        return;
    }


    selectedScheme = null;


    schemeDetailsView.classList.remove(
        "show"
    );


    schemeDetailsView.setAttribute(
        "aria-hidden",
        "true"
    );


    schemeList.style.display =
        "grid";


    schemeInformationPanel.style.display =
        "block";


    schemeEligibilityPanel.classList.remove(
        "show"
    );


    schemeEligibilityPanel.setAttribute(
        "aria-hidden",
        "true"
    );


    restoreEligibilityButton();


    clearEligibilityForm();


    const schemesSection =
        document.getElementById(
            "schemes"
        );


    if (schemesSection) {

        schemesSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

}


if (schemeBackButton) {

    schemeBackButton.addEventListener(
        "click",
        closeSchemeDetails
    );

}


/* ================= ELIGIBILITY ================= */

const originalEligibilityButtonHTML =
    mainEligibilityTestBtn
        ? mainEligibilityTestBtn.innerHTML
        : `
            <span>
                Eligibility Test
            </span>

            <span>
                →
            </span>
        `;


function restoreEligibilityButton() {

    if (!mainEligibilityTestBtn) {
        return;
    }


    mainEligibilityTestBtn.innerHTML =
        originalEligibilityButtonHTML;

}


if (mainEligibilityTestBtn) {

    mainEligibilityTestBtn.addEventListener(
        "click",
        function () {

            if (!selectedScheme) {
                return;
            }


            if (
                schemeEligibilityPanel.classList.contains(
                    "show"
                )
            ) {

                schemeEligibilityPanel.classList.remove(
                    "show"
                );


                schemeEligibilityPanel.setAttribute(
                    "aria-hidden",
                    "true"
                );


                schemeInformationPanel.style.display =
                    "block";


                restoreEligibilityButton();


                clearEligibilityForm();


                schemeInformationPanel.scrollIntoView({
                    behavior: "smooth",
                    block: "nearest"
                });


                return;

            }


            schemeInformationPanel.style.display =
                "none";


            eligibilitySchemeTitle.textContent =
                selectedScheme.name;


            clearEligibilityResult();


            schemeEligibilityPanel.classList.add(
                "show"
            );


            schemeEligibilityPanel.setAttribute(
                "aria-hidden",
                "false"
            );


            mainEligibilityTestBtn.innerHTML = `
                <span>
                    ←
                </span>

                <span>
                    Back
                </span>
            `;


            schemeEligibilityPanel.scrollIntoView({
                behavior: "smooth",
                block: "nearest"
            });

        }
    );

}


/* ================= ELIGIBILITY FORM ================= */

if (eligibilityForm) {

    eligibilityForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            if (!selectedScheme) {
                showEligibilityResult("Please select a scheme first.");
                return;
            }

            const profile = {
                age: eligibilityAge ? Number(eligibilityAge.value) : null,
                state: eligibilityState ? eligibilityState.value.trim() : "",
                occupation: eligibilityOccupation ? eligibilityOccupation.value.trim() : "",
                income: eligibilityIncome ? Number(eligibilityIncome.value) : null,
                category: eligibilityCategory ? eligibilityCategory.value : "",
                documents_available: eligibilityDocuments ? eligibilityDocuments.value : ""
            };

            if (
                !profile.age ||
                !profile.state ||
                !profile.occupation ||
                profile.income === null ||
                profile.income === undefined ||
                !eligibilityDocuments.value
            ) {
                showEligibilityResult("Please complete the required profile details.");
                return;
            }

            const button = eligibilityForm.querySelector(".eligibility-submit-btn");
            const original = button ? button.innerHTML : "";

            if (button) {
                button.disabled = true;
                button.innerHTML = "Checking...";
            }

            try {
                const response = await fetch(
                    `${API_BASE_URL}/api/schemes/eligibility-check`,
                    {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({
                            scheme: selectedScheme,
                            profile: profile
                        })
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Eligibility check failed.");
                }

                showEligibilityResult(
                    data.message ||
                    "Your profile was checked. Please verify final eligibility with the official scheme authority."
                );

            } catch (error) {
                // Fallback: give the Gemini assistant enough context to explain eligibility.
                try {
                    const prompt =
                        `Check my possible eligibility for the government scheme "${selectedScheme.name}".
My details: age ${profile.age}, state ${profile.state}, occupation ${profile.occupation},
annual family income ₹${profile.income}, category ${profile.category || "not provided"},
documents available: ${profile.documents_available}.
Explain which eligibility conditions I appear to meet, which are uncertain, what documents are needed,
and what I should do next. Do not make a final legal/government eligibility determination.`;

                    smartTalkInput.value = prompt;
                    openSmartTalk();
                    showEligibilityResult("Opening CivicAssist AI for a detailed eligibility check...");
                } catch (fallbackError) {
                    showEligibilityResult(error.message);
                }
            } finally {
                if (button) {
                    button.disabled = false;
                    button.innerHTML = original;
                }
            }
        }
    );
}

/* ================= ELIGIBILITY RESULT ================= */

function showEligibilityResult(
    message
) {

    if (!eligibilityResultMessage) {
        return;
    }


    clearTimeout(
        eligibilityResultTimeout
    );


    eligibilityResultMessage.textContent =
        message;


    eligibilityResultMessage.classList.add(
        "show"
    );


    eligibilityResultTimeout =
        setTimeout(
            function () {

                clearEligibilityResult();

            },
            4500
        );

}


function clearEligibilityResult() {

    if (!eligibilityResultMessage) {
        return;
    }


    clearTimeout(
        eligibilityResultTimeout
    );


    eligibilityResultMessage.textContent =
        "";


    eligibilityResultMessage.classList.remove(
        "show"
    );

}


/* ================= CLEAR ELIGIBILITY ================= */

function clearEligibilityForm() {

    if (eligibilityAge) eligibilityAge.value = "";
    if (eligibilityState) eligibilityState.value = "";
    if (eligibilityOccupation) eligibilityOccupation.value = "";
    if (eligibilityIncome) eligibilityIncome.value = "";
    if (eligibilityCategory) eligibilityCategory.value = "";
    if (eligibilityDocuments) eligibilityDocuments.value = "";


    clearEligibilityResult();

}


if (eligibilityClearBtn) {

    eligibilityClearBtn.addEventListener(
        "click",
        clearEligibilityForm
    );

}


/* ================= SMART TALK OPEN ================= */

function openSmartTalk() {

    if (!smartTalkPage) {
        return;
    }


    smartTalkOpen = true;


    smartTalkPage.classList.add(
        "show"
    );


    smartTalkPage.setAttribute(
        "aria-hidden",
        "false"
    );


    document.body.style.overflow =
        "hidden";


    setTimeout(
        function () {

            if (smartTalkInput) {
                smartTalkInput.focus();
            }

        },
        350
    );

}


function closeSmartTalk() {

    if (!smartTalkPage) {
        return;
    }


    smartTalkOpen = false;


    closeSmartTalkLanguagePopup();


    smartTalkPage.classList.remove(
        "show"
    );


    smartTalkPage.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.style.overflow =
        "";

}


if (findSchemesBtn) {

    findSchemesBtn.addEventListener(
        "click",
        openSmartTalk
    );

}


if (smartTalkExitBtn) {

    smartTalkExitBtn.addEventListener(
        "click",
        closeSmartTalk
    );

}


/* ================= AI MARKDOWN RENDERER ================= */

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function inlineCivicMarkdown(value) {
    let text = escapeHtml(value);
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\*(.+?)\*/g, "<em>$1</em>");
    text = text.replace(/`(.+?)`/g, "<code>$1</code>");
    return text;
}

function renderCivicMarkdown(markdown) {
    const lines = String(markdown || "").replace(/\r/g, "").split("\n");
    let html = "";
    let inTable = false;
    let inList = false;

    function closeTable() {
        if (inTable) {
            html += "</tbody></table>";
            inTable = false;
        }
    }

    function closeList() {
        if (inList) {
            html += "</ul>";
            inList = false;
        }
    }

    for (const rawLine of lines) {
        const line = rawLine.trim();

        if (!line) {
            closeTable();
            closeList();
            continue;
        }

        if (line.startsWith("|") && line.endsWith("|")) {
            const cells = line.slice(1, -1).split("|").map(x => x.trim());

            if (cells.every(cell => /^:?-{3,}:?$/.test(cell))) {
                continue;
            }

            if (!inTable) {
                closeList();
                html += "<table class=\"ai-table\"><thead><tr>";
                cells.forEach(cell => {
                    html += `<th>${inlineCivicMarkdown(cell)}</th>`;
                });
                html += "</tr></thead><tbody>";
                inTable = true;
            } else {
                html += "<tr>";
                cells.forEach(cell => {
                    html += `<td>${inlineCivicMarkdown(cell)}</td>`;
                });
                html += "</tr>";
            }
            continue;
        }

        closeTable();

        const heading = line.match(/^(#{1,4})\s+(.+)$/);
        if (heading) {
            closeList();
            const level = Math.min(4, heading[1].length);
            html += `<h${level}>${inlineCivicMarkdown(heading[2])}</h${level}>`;
            continue;
        }

        if (/^[-*]\s+/.test(line)) {
            if (!inList) {
                html += "<ul>";
                inList = true;
            }
            html += `<li>${inlineCivicMarkdown(line.replace(/^[-*]\s+/, ""))}</li>`;
            continue;
        }

        closeList();
        html += `<p>${inlineCivicMarkdown(line)}</p>`;
    }

    closeTable();
    closeList();
    return html;
}


/* ================= CHAT MESSAGE ================= */

function addChatMessage(
    message,
    type
) {

    if (!chatMessages) {
        return;
    }


    const messageWrapper =
        document.createElement(
            "div"
        );


    messageWrapper.className =
        `chat-message ${type}-message`;


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "chat-avatar";


    avatar.textContent =
        type === "user"
            ? "👤"
            : "✨";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "chat-bubble";


    const strong =
        document.createElement(
            "strong"
        );


    strong.textContent =
        type === "user"
            ? "You"
            : "CivicAssist AI";


    const content =
        document.createElement("div");

    content.className = "chat-content";

    if (type === "ai") {
        content.innerHTML = renderCivicMarkdown(message);
    } else {
        const paragraph = document.createElement("p");
        paragraph.textContent = message;
        content.appendChild(paragraph);
    }

    bubble.appendChild(strong);
    bubble.appendChild(content);


    messageWrapper.appendChild(
        avatar
    );


    messageWrapper.appendChild(
        bubble
    );


    chatMessages.appendChild(
        messageWrapper
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* ================= FRONTEND RESPONSE ================= */

function getFrontendResponse(
    question
) {

    const lower =
        question
            .toLowerCase()
            .trim();


    if (
        lower.includes("education") ||
        lower.includes("student") ||
        lower.includes("scholarship")
    ) {

        return (
            "For education-related support, CivicAssist can help you explore schemes such as Samagra Shiksha, PM POSHAN and NMMSS. The actual AI information service will be connected later."
        );

    }


    if (
        lower.includes("health") ||
        lower.includes("medical")
    ) {

        return (
            "For healthcare support, CivicAssist includes schemes such as Ayushman Bharat – PM-JAY, Ayushman Arogya Mandirs and Jan Aushadhi Scheme. Detailed AI-based information will be connected later."
        );

    }


    if (
        lower.includes("farmer") ||
        lower.includes("farming") ||
        lower.includes("agriculture")
    ) {

        return (
            "For farmers, CivicAssist includes PM-KISAN, PMFBY and Kisan Credit Card. The future AI version will provide more personalised information."
        );

    }


    if (
        lower.includes("job") ||
        lower.includes("employment") ||
        lower.includes("career")
    ) {

        return (
            "For employment support, CivicAssist includes MGNREGA, PMKVY and National Career Service. The actual information-gathering AI will be connected later."
        );

    }


    if (
        lower.includes("home") ||
        lower.includes("housing")
    ) {

        return (
            "For housing support, CivicAssist includes PMAY-G, PMAY-U and PM SVANidhi. More intelligent scheme guidance will be added later."
        );

    }


    if (
        lower.includes("hello") ||
        lower.includes("hi") ||
        lower.includes("hey")
    ) {

        return (
            "Hello! I am Smart Talk, the CivicAssist information assistant. The chatbot interface is ready, and the real AI information system will be connected later."
        );

    }


    return (
        "I received your question. The Smart Talk frontend is ready, but the real AI information-gathering functionality has not been connected yet."
    );

}


/* ================= SMART TALK FORM ================= */

if (smartTalkForm) {

    smartTalkForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const message =
                smartTalkInput.value.trim();


            if (!message) {
                return;
            }


            addChatMessage(
                message,
                "user"
            );


            smartTalkInput.value =
                "";


            /* Make sure there is an active chat before we call the backend. */

            if (!currentChatId) {

                createNewChat();

            }


            const currentChat =
                getCurrentChat();


            const typingBubble =
                showTypingIndicator();


            try {

                const result =
                    await sendMessageToBackend(
                        message,
                        currentChat
                            ? currentChat.conversationId
                            : null
                    );


                removeTypingIndicator(
                    typingBubble
                );


                if (
                    currentChat &&
                    result.conversation_id
                ) {

                    currentChat.conversationId =
                        result.conversation_id;

                    saveChatHistory();

                }


                addChatMessage(
                    result.response,
                    "ai"
                );

            } catch (error) {

                removeTypingIndicator(
                    typingBubble
                );


                console.error(
                    "CivicAssist backend request failed.",
                    error
                );


                addChatMessage(
                    "Sorry, I couldn't reach the CivicAssist server. " +
                    "Please make sure the backend is running and try again. " +
                    `(${error.message})`,
                    "ai"
                );

            }

        }
    );

}


/* ================= TYPING INDICATOR ================= */

function showTypingIndicator() {

    if (!chatMessages) {
        return null;
    }


    const messageWrapper =
        document.createElement(
            "div"
        );


    messageWrapper.className =
        "chat-message ai-message smart-talk-typing";


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "chat-avatar";


    avatar.textContent =
        "✨";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "chat-bubble";


    const strong =
        document.createElement(
            "strong"
        );


    strong.textContent =
        "CivicAssist AI";


    const paragraph =
        document.createElement(
            "p"
        );


    paragraph.textContent =
        "Thinking...";


    bubble.appendChild(
        strong
    );


    bubble.appendChild(
        paragraph
    );


    messageWrapper.appendChild(
        avatar
    );


    messageWrapper.appendChild(
        bubble
    );


    chatMessages.appendChild(
        messageWrapper
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return messageWrapper;

}


function removeTypingIndicator(
    typingBubble
) {

    if (
        typingBubble &&
        typingBubble.parentNode
    ) {

        typingBubble.remove();

    }

}


/* ================= SMART TALK SUGGESTIONS ================= */

smartTalkSuggestions.forEach(
    suggestion => {

        suggestion.addEventListener(
            "click",
            function () {

                if (!smartTalkInput) {
                    return;
                }


                smartTalkInput.value =
                    this.textContent.trim();


                smartTalkInput.focus();

            }
        );

    }
);


/* ================= FILE UPLOAD ================= */

if (
    smartTalkUploadBtn &&
    smartTalkFileInput
) {

    smartTalkUploadBtn.addEventListener(
        "click",
        function () {

            smartTalkFileInput.click();

        }
    );


    smartTalkFileInput.addEventListener(
        "change",
        async function () {

            const file =
                this.files[0];


            if (!file) {
                return;
            }


            addChatMessage(
                `Selected file: ${file.name}`,
                "user"
            );


            this.value =
                "";


            const typingBubble =
                showTypingIndicator();


            try {

                const result =
                    await uploadDocumentToBackend(
                        file
                    );


                removeTypingIndicator(
                    typingBubble
                );


                addChatMessage(
                    result.message ||
                    `"${file.name}" was uploaded successfully.`,
                    "ai"
                );

            } catch (error) {

                removeTypingIndicator(
                    typingBubble
                );


                console.error(
                    "Document upload failed.",
                    error
                );


                addChatMessage(
                    "Sorry, I couldn't upload that file. " +
                    `(${error.message})`,
                    "ai"
                );

            }

        }
    );

}


/* ================= LANGUAGE POPUP ================= */

function openSmartTalkLanguagePopup() {

    if (!smartTalkLanguageOverlay) {
        return;
    }


    const currentLanguage =
        localStorage.getItem(
            "civicAssistLanguage"
        ) || "English";


    smartTalkLanguageOptions.forEach(
        option => {

            option.classList.toggle(
                "selected",
                option.dataset.language ===
                    currentLanguage
            );

        }
    );


    smartTalkLanguageOverlay.classList.add(
        "show"
    );


    smartTalkLanguageOverlay.setAttribute(
        "aria-hidden",
        "false"
    );

}


function closeSmartTalkLanguagePopup() {

    if (!smartTalkLanguageOverlay) {
        return;
    }


    smartTalkLanguageOverlay.classList.remove(
        "show"
    );


    smartTalkLanguageOverlay.setAttribute(
        "aria-hidden",
        "true"
    );

}


if (smartTalkLanguageBtn) {

    smartTalkLanguageBtn.addEventListener(
        "click",
        openSmartTalkLanguagePopup
    );

}


if (smartTalkLanguageCloseBtn) {

    smartTalkLanguageCloseBtn.addEventListener(
        "click",
        closeSmartTalkLanguagePopup
    );

}


if (smartTalkLanguageOverlay) {

    smartTalkLanguageOverlay.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                smartTalkLanguageOverlay
            ) {

                closeSmartTalkLanguagePopup();

            }

        }
    );

}


smartTalkLanguageOptions.forEach(
    option => {

        option.addEventListener(
            "click",
            function () {

                const selectedLanguage =
                    this.dataset.language;


                localStorage.setItem(
                    "civicAssistLanguage",
                    selectedLanguage
                );


                const profileString =
                    localStorage.getItem(
                        "civicAssistProfile"
                    );


                if (profileString) {

                    try {

                        const profile =
                            JSON.parse(
                                profileString
                            );


                        profile.language =
                            selectedLanguage;


                        localStorage.setItem(
                            "civicAssistProfile",
                            JSON.stringify(
                                profile
                            )
                        );

                    } catch (error) {

                        console.error(
                            "Unable to update profile language.",
                            error
                        );

                    }

                }


                smartTalkLanguageOptions.forEach(
                    languageOption => {

                        languageOption.classList.toggle(
                            "selected",
                            languageOption ===
                                this
                        );

                    }
                );


                closeSmartTalkLanguagePopup();

            }
        );

    }
);


/* ================= CHAT HISTORY ================= */

const CHAT_HISTORY_STORAGE_KEY =
    "civicAssistChatHistory";


let chatHistory = [];

let currentChatId = null;


/* ================= LOAD SAVED HISTORY ================= */

function loadChatHistory() {

    try {

        const savedHistory =
            localStorage.getItem(
                CHAT_HISTORY_STORAGE_KEY
            );


        if (savedHistory) {

            chatHistory =
                JSON.parse(
                    savedHistory
                );

        }

    } catch (error) {

        console.error(
            "Unable to load chat history.",
            error
        );

        chatHistory = [];

    }


    if (!Array.isArray(chatHistory)) {

        chatHistory = [];

    }

}


/* ================= SAVE HISTORY ================= */

function saveChatHistory() {

    try {

        localStorage.setItem(
            CHAT_HISTORY_STORAGE_KEY,
            JSON.stringify(
                chatHistory
            )
        );

    } catch (error) {

        console.error(
            "Unable to save chat history.",
            error
        );

    }

}


/* ================= CREATE NEW CHAT ================= */

function createNewChat() {

    const newChat = {

        id:
            Date.now().toString(),

        title:
            "New conversation",

        messages: [],

        /*
           conversationId ties this local chat thread to the
           conversation on the CivicAssist backend once the
           backend has assigned one.
        */

        conversationId:
            null

    };


    chatHistory.unshift(
        newChat
    );


    currentChatId =
        newChat.id;


    saveChatHistory();

    renderChatHistory();

}


/* ================= GET CURRENT CHAT ================= */

function getCurrentChat() {

    return chatHistory.find(
        chat =>
            chat.id ===
            currentChatId
    );

}


/* ================= UPDATE CHAT TITLE ================= */

function updateChatTitle(
    chat
) {

    if (
        !chat ||
        !chat.messages ||
        !chat.messages.length
    ) {

        return;

    }


    const firstUserMessage =
        chat.messages.find(
            message =>
                message.type ===
                "user"
        );


    if (!firstUserMessage) {

        return;

    }


    let title =
        firstUserMessage.text
            .trim();


    if (!title) {

        return;

    }


    if (title.length > 32) {

        title =
            title.substring(
                0,
                32
            ) + "...";

    }


    chat.title =
        title;

}


/* ================= RENDER CHAT HISTORY ================= */

function renderChatHistory() {

    if (!smartTalkHistoryList) {
        return;
    }


    smartTalkHistoryList.innerHTML = "";


    chatHistory.forEach(
        chat => {

            /* ================= HISTORY ITEM WRAPPER ================= */

            const historyWrapper =
                document.createElement(
                    "div"
                );


            historyWrapper.className =
                "smart-talk-history-wrapper";


            /* ================= OPEN CHAT BUTTON ================= */

            const historyItem =
                document.createElement(
                    "button"
                );


            historyItem.type =
                "button";


            historyItem.className =
                "smart-talk-history-item";


            if (
                chat.id ===
                currentChatId
            ) {

                historyItem.classList.add(
                    "active"
                );

            }


            const icon =
                document.createElement(
                    "span"
                );


            icon.className =
                "smart-talk-history-item-icon";


            icon.textContent =
                "💬";


            const text =
                document.createElement(
                    "span"
                );


            text.className =
                "smart-talk-history-item-text";


            text.textContent =
                chat.title ||
                "New conversation";


            historyItem.appendChild(
                icon
            );


            historyItem.appendChild(
                text
            );


            /* ================= OPEN SAVED CHAT ================= */

            historyItem.addEventListener(
                "click",
                function () {

                    openSavedChat(
                        chat.id
                    );

                }
            );


            /* ================= DELETE BUTTON ================= */

            const deleteButton =
                document.createElement(
                    "button"
                );


            deleteButton.type =
                "button";


            deleteButton.className =
                "smart-talk-history-delete";


            deleteButton.title =
                "Delete conversation";


            deleteButton.setAttribute(
                "aria-label",
                "Delete conversation"
            );


            deleteButton.innerHTML =
                "🗑";


            /* ================= DELETE CHAT ================= */

            deleteButton.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();


                    deleteChatHistory(
                        chat.id
                    );

                }
            );


            /* ================= ADD ELEMENTS ================= */

            historyWrapper.appendChild(
                historyItem
            );


            historyWrapper.appendChild(
                deleteButton
            );


            smartTalkHistoryList.appendChild(
                historyWrapper
            );

        }
    );

}


/* ================= DELETE CHAT HISTORY ================= */

function deleteChatHistory(chatId) {

    const chatIndex =
        chatHistory.findIndex(
            chat => chat.id === chatId
        );


    if (chatIndex === -1) {
        return;
    }


    const chatToDelete =
        chatHistory[chatIndex];


    showDeleteConfirmation(
        chatToDelete,
        chatId
    );

}


/* ================= DELETE CONFIRMATION BOX ================= */

function showDeleteConfirmation(
    chat,
    chatId
) {

    /* Remove existing dialog if any */

    const existingDialog =
        document.getElementById(
            "deleteHistoryModal"
        );


    if (existingDialog) {
        existingDialog.remove();
    }


    /* Create modal */

    const modal =
        document.createElement(
            "div"
        );


    modal.id =
        "deleteHistoryModal";


    modal.className =
        "delete-history-modal";


    modal.innerHTML = `

        <div class="delete-history-overlay"></div>

        <div class="delete-history-box">

            <div class="delete-history-icon">
                🗑️
            </div>

            <h3>
                Delete conversation?
            </h3>

            <p>
                Are you sure you want to delete
                <strong>
                    "${escapeDeleteHistoryText(
                        chat.title ||
                        "New conversation"
                    )}"
                </strong>
                ?
            </p>

            <span class="delete-history-warning">
                This conversation will be permanently removed.
            </span>

            <div class="delete-history-actions">

                <button
                    type="button"
                    class="delete-history-cancel"
                    id="cancelDeleteHistory"
                >
                    Cancel
                </button>

                <button
                    type="button"
                    class="delete-history-confirm"
                    id="confirmDeleteHistory"
                >
                    Delete
                </button>

            </div>

        </div>

    `;


    document.body.appendChild(
        modal
    );


    /* Small delay for animation */

    requestAnimationFrame(
        () => {

            modal.classList.add(
                "show"
            );

        }
    );


    /* ================= CANCEL ================= */

    const cancelButton =
        document.getElementById(
            "cancelDeleteHistory"
        );


    cancelButton.addEventListener(
        "click",
        function () {

            closeDeleteHistoryModal(
                modal
            );

        }
    );


    /* ================= CONFIRM DELETE ================= */

    const confirmButton =
        document.getElementById(
            "confirmDeleteHistory"
        );


    confirmButton.addEventListener(
        "click",
        function () {

            performDeleteChatHistory(
                chatId,
                modal
            );

        }
    );


    /* ================= CLICK OUTSIDE ================= */

    const overlay =
        modal.querySelector(
            ".delete-history-overlay"
        );


    overlay.addEventListener(
        "click",
        function () {

            closeDeleteHistoryModal(
                modal
            );

        }
    );


    /* ================= ESC KEY ================= */

    function handleEscape(
        event
    ) {

        if (
            event.key ===
            "Escape"
        ) {

            closeDeleteHistoryModal(
                modal
            );

            document.removeEventListener(
                "keydown",
                handleEscape
            );

        }

    }


    document.addEventListener(
        "keydown",
        handleEscape
    );

}


/* ================= PERFORM DELETE ================= */

function performDeleteChatHistory(
    chatId,
    modal
) {

    const chatIndex =
        chatHistory.findIndex(
            chat => chat.id === chatId
        );


    if (chatIndex === -1) {

        closeDeleteHistoryModal(
            modal
        );

        return;

    }


    /* Remove conversation */

    chatHistory.splice(
        chatIndex,
        1
    );


    /* Save updated history */

    saveChatHistory();


    /* Close dialog */

    closeDeleteHistoryModal(
        modal
    );


    /* If current conversation was deleted */

    if (
        currentChatId === chatId
    ) {

        if (
            chatHistory.length > 0
        ) {

            currentChatId =
                chatHistory[0].id;


            renderChatHistory();

            openSavedChat(
                currentChatId
            );

        } else {

            currentChatId =
                null;


            createNewChat();

        }

    } else {

        renderChatHistory();

    }

}


/* ================= CLOSE DELETE MODAL ================= */

function closeDeleteHistoryModal(
    modal
) {

    if (!modal) {
        return;
    }


    modal.classList.remove(
        "show"
    );


    setTimeout(
        () => {

            if (
                modal &&
                modal.parentNode
            ) {

                modal.remove();

            }

        },
        200
    );

}


/* ================= SAFE HISTORY TITLE ================= */

function escapeDeleteHistoryText(
    text
) {

    return String(text)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}
/* ================= ADD MESSAGE TO SCREEN ================= */

function displaySavedMessage(
    message,
    type
) {

    if (!chatMessages) {

        return;

    }


    const messageWrapper =
        document.createElement(
            "div"
        );


    messageWrapper.className =
        `chat-message ${type}-message`;


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "chat-avatar";


    avatar.textContent =
        type === "user"
            ? "👤"
            : "✨";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "chat-bubble";


    const strong =
        document.createElement(
            "strong"
        );


    strong.textContent =
        type === "user"
            ? "You"
            : "CivicAssist AI";


    const content =
        document.createElement("div");

    content.className = "chat-content";

    if (type === "ai") {
        content.innerHTML = renderCivicMarkdown(message);
    } else {
        const paragraph = document.createElement("p");
        paragraph.textContent = message;
        content.appendChild(paragraph);
    }

    bubble.appendChild(strong);
    bubble.appendChild(content);


    messageWrapper.appendChild(
        avatar
    );


    messageWrapper.appendChild(
        bubble
    );


    chatMessages.appendChild(
        messageWrapper
    );

}


/* ================= OPEN SAVED CHAT ================= */

function openSavedChat(
    chatId
) {

    const chat =
        chatHistory.find(
            item =>
                item.id ===
                chatId
        );


    if (!chat || !chatMessages) {

        return;

    }


    currentChatId =
        chat.id;


    chatMessages.innerHTML =
        "";


    if (
        !chat.messages ||
        !chat.messages.length
    ) {

        chatMessages.innerHTML = `
            <div class="chat-message ai-message">

                <div class="chat-avatar">
                    ✨
                </div>

                <div class="chat-bubble">

                    <strong>
                        CivicAssist AI
                    </strong>

                    <p>
                        Hello! I am Smart Talk.
                        Ask me anything about government
                        schemes and citizen services.
                    </p>

                </div>

            </div>
        `;

    } else {

        chat.messages.forEach(
            message => {

                displaySavedMessage(
                    message.text,
                    message.type
                );

            }
        );

    }


    renderChatHistory();


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* ================= OVERRIDE ADD CHAT MESSAGE ================= */

function addChatMessage(
    message,
    type
) {

    if (!chatMessages) {

        return;

    }


    /*
       If there is no active chat,
       create one automatically.
    */

    if (!currentChatId) {

        createNewChat();

    }


    const currentChat =
        getCurrentChat();


    if (!currentChat) {

        return;

    }


    /* Display message */

    displaySavedMessage(
        message,
        type
    );


    /* Save message */

    currentChat.messages.push({

        type:
            type,

        text:
            message,

        time:
            new Date().toISOString()

    });


    /* Automatically use first user
       message as conversation title */

    if (
        type === "user"
    ) {

        updateChatTitle(
            currentChat
        );

    }


    saveChatHistory();

    renderChatHistory();


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* ================= NEW CHAT BUTTON ================= */

if (smartTalkNewChatBtn) {

    smartTalkNewChatBtn.addEventListener(
        "click",
        function () {

            if (!chatMessages) {

                return;

            }


            createNewChat();


            chatMessages.innerHTML = `
                <div class="chat-message ai-message">

                    <div class="chat-avatar">
                        ✨
                    </div>

                    <div class="chat-bubble">

                        <strong>
                            CivicAssist AI
                        </strong>

                        <p>
                            Hello! I am Smart Talk.
                            Ask me anything about government
                            schemes and citizen services.
                        </p>

                    </div>

                </div>
            `;


            if (smartTalkInput) {

                smartTalkInput.value =
                    "";

                smartTalkInput.focus();

            }

        }
    );

}


/* ================= INITIALIZE CHAT HISTORY ================= */

loadChatHistory();


/*
   If old chats exist, open the latest one.
   Otherwise create the first conversation.
*/

if (chatHistory.length > 0) {

    currentChatId =
        chatHistory[0].id;

    renderChatHistory();

} else {

    createNewChat();

}


/* ================= NAVIGATION ================= */

const navLinks =
    document.querySelectorAll(
        ".nav-links a"
    );


navLinks.forEach(
    link => {

        link.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                const sectionId =
                    this.dataset.section;


                const target =
                    document.getElementById(
                        sectionId
                    );


                if (!target) {
                    return;
                }


                if (smartTalkOpen) {

                    closeSmartTalk();

                }


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });


                navLinks.forEach(
                    navLink =>
                        navLink.classList.remove(
                            "active"
                        )
                );


                this.classList.add(
                    "active"
                );

            }
        );

    }
);


/* ================= ACTIVE NAVIGATION ================= */

const trackedSections = [

    "home",
    "schemes",
    "nearby-services",
    "what-civicassist-do",
    "about",
    "contact"

];


window.addEventListener(
    "scroll",
    function () {

        if (smartTalkOpen) {
            return;
        }


        const scrollPosition =
            window.scrollY + 160;


        let currentSection =
            "home";


        trackedSections.forEach(
            sectionId => {

                const section =
                    document.getElementById(
                        sectionId
                    );


                if (
                    section &&
                    section.offsetTop <=
                    scrollPosition
                ) {

                    currentSection =
                        sectionId;

                }

            }
        );


        navLinks.forEach(
            link => {

                link.classList.toggle(
                    "active",
                    link.dataset.section ===
                    currentSection
                );

            }
        );

    }
);


/* ================= ESCAPE KEY ================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key !==
            "Escape"
        ) {

            return;

        }


        closeLoginModalFunction();

        closeLogoutDialog();

        hideLoginSuccess();

        closeSmartTalkLanguagePopup();


        if (smartTalkOpen) {

            closeSmartTalk();

        }

    }
);


/* ================= INITIAL STATE ================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateLoginButton();

    }
);


updateLoginButton();


/* ================= NEARBY SERVICES ================= */

let civicAssistMap = null;
let nearbyUserMarker = null;
let nearbyPlaceMarkers = [];
let nearbyAccuracyCircle = null;
let nearbyUserLocation = null;
let nearbySelectedCategory = "lawyers";
let nearbyMapToken = "";

const NEARBY_CATEGORY_LABELS = {
    lawyers: "lawyers and advocates",
    government: "government offices",
    service_centers: "government service centres",
    legal_aid: "legal aid centres",
    police: "police stations",
    courthouse: "courts and courthouses"
};

function setNearbyStatus(message, isError = false) {
    const el = document.getElementById("nearbyStatus");
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("error", isError);
}

function escapeNearbyHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
    }[char]));
}

function clearNearbyMarkers() {
    nearbyPlaceMarkers.forEach(marker => marker.remove());
    nearbyPlaceMarkers = [];
    if (nearbyUserMarker) {
        nearbyUserMarker.remove();
        nearbyUserMarker = null;
    }
    if (nearbyAccuracyCircle) {
        nearbyAccuracyCircle.remove();
        nearbyAccuracyCircle = null;
    }
}

function createUserMarkerElement() {
    const el = document.createElement("div");
    el.className = "nearby-user-marker";
    el.title = "Your current location";
    return el;
}

function createPlaceMarkerElement(number) {
    const el = document.createElement("div");
    el.className = "nearby-place-marker";
    el.textContent = String(number);
    return el;
}

function ensureNearbyMap() {
    if (!nearbyMapToken || !window.mapboxgl) return false;
    const mapEl = document.getElementById("nearbyMap");
    if (!mapEl) return false;

    if (!civicAssistMap) {
        mapboxgl.accessToken = nearbyMapToken;
        civicAssistMap = new mapboxgl.Map({
            container: mapEl,
            style: "mapbox://styles/mapbox/streets-v12",
            center: [nearbyUserLocation?.lng || 80.2707, nearbyUserLocation?.lat || 13.0827],
            zoom: 13,
            attributionControl: true,
            cooperativeGestures: true
        });
        civicAssistMap.addControl(new mapboxgl.NavigationControl(), "top-right");
    }
    return true;
}

function renderNearbyMap(places = []) {
    if (!nearbyUserLocation || !ensureNearbyMap()) return;

    const center = [nearbyUserLocation.lng, nearbyUserLocation.lat];
    civicAssistMap.resize();
    civicAssistMap.setCenter(center);
    civicAssistMap.setZoom(13);

    clearNearbyMarkers();

    const userPopup = new mapboxgl.Popup({ offset: 18 }).setHTML("<strong>Your current location</strong>");
    nearbyUserMarker = new mapboxgl.Marker({ element: createUserMarkerElement() })
        .setLngLat(center)
        .setPopup(userPopup)
        .addTo(civicAssistMap);

    if (nearbyUserLocation.accuracy && nearbyUserLocation.accuracy < 5000) {
        // Mapbox GL does not provide a simple DOM circle with meter radius;
        // show accuracy in the status and keep the user marker visually clear.
    }

    const validPlaces = places.filter(p => p.latitude != null && p.longitude != null);
    const bounds = new mapboxgl.LngLatBounds();
    bounds.extend(center);

    validPlaces.forEach((place, index) => {
        const popupHtml = `<strong>${escapeNearbyHtml(place.name)}</strong><br>${escapeNearbyHtml(place.address || "Address unavailable")}<br><small>${(Number(place.distance) / 1000).toFixed(1)} km away</small>`;
        const marker = new mapboxgl.Marker({ element: createPlaceMarkerElement(index + 1) })
            .setLngLat([place.longitude, place.latitude])
            .setPopup(new mapboxgl.Popup({ offset: 18 }).setHTML(popupHtml))
            .addTo(civicAssistMap);
        nearbyPlaceMarkers.push(marker);
        bounds.extend([place.longitude, place.latitude]);
    });

    if (validPlaces.length) {
        civicAssistMap.fitBounds(bounds, { padding: 70, maxZoom: 15, duration: 500 });
    }

    setTimeout(() => civicAssistMap?.resize(), 100);
    setTimeout(() => civicAssistMap?.resize(), 500);
}

function renderNearbyResults(places) {
    const container = document.getElementById("nearbyResults");
    if (!container) return;
    if (!places.length) {
        container.innerHTML = `<div class="nearby-empty">No matching ${escapeNearbyHtml(NEARBY_CATEGORY_LABELS[nearbySelectedCategory] || "places")} were found within this radius. Try 10 km or 25 km.</div>`;
        return;
    }

    container.innerHTML = places.map((place, index) => {
        const mapUrl = `https://www.openstreetmap.org/?mlat=${encodeURIComponent(place.latitude)}&mlon=${encodeURIComponent(place.longitude)}#map=18/${place.latitude}/${place.longitude}`;
        const directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(nearbyUserLocation.lat + "," + nearbyUserLocation.lng)}&destination=${encodeURIComponent(place.latitude + "," + place.longitude)}`;
        const phone = place.phone ? `<a href="tel:${escapeNearbyHtml(place.phone)}">📞 ${escapeNearbyHtml(place.phone)}</a>` : "";
        const website = place.website ? `<a href="${escapeNearbyHtml(place.website)}" target="_blank" rel="noopener">Website</a>` : "";
        const distance = Number.isFinite(Number(place.distance)) ? `${(Number(place.distance) / 1000).toFixed(1)} km` : "";

        return `<article class="nearby-card">
            <div class="nearby-card-number">${index + 1}</div>
            <div class="nearby-card-body">
                <h3>${escapeNearbyHtml(place.name)}</h3>
                <p>${escapeNearbyHtml(place.address || "Address unavailable")}</p>
                <div class="nearby-meta">${distance} ${phone} ${website}</div>
                <div class="nearby-actions">
                    <a href="${mapUrl}" target="_blank" rel="noopener">View location</a>
                    <a href="${directionsUrl}" target="_blank" rel="noopener">Directions</a>
                </div>
            </div>
        </article>`;
    }).join("");
}

async function loadNearbyMapConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/nearby/config`);
        const data = await response.json();
        nearbyMapToken = data.mapbox_access_token || "";
        if (!nearbyMapToken) {
            setNearbyStatus("Mapbox token is missing. Add MAPBOX_ACCESS_TOKEN to Backend/.env and restart the backend.", true);
        }
    } catch (error) {
        setNearbyStatus("Could not connect to the CivicAssist backend. Start the backend on port 8000.", true);
    }
}

async function searchNearbyServices() {
    if (!nearbyUserLocation) {
        setNearbyStatus("Please allow location access first.", true);
        return;
    }

    const radius = Number(document.getElementById("nearbyRadius")?.value || 5000);
    setNearbyStatus("Searching nearby services…");

    try {
        const response = await fetch(`${API_BASE_URL}/api/nearby/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                latitude: nearbyUserLocation.lat,
                longitude: nearbyUserLocation.lng,
                category: nearbySelectedCategory,
                radius
            })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Nearby search failed.");

        renderNearbyResults(data.places || []);
        renderNearbyMap(data.places || []);
        setNearbyStatus(`${data.count || 0} result(s) found within ${radius / 1000} km • ${data.provider || "Mapbox"}`);
    } catch (error) {
        setNearbyStatus(error.message || "Unable to search nearby services.", true);
    }
}

function getNearbyUserLocation() {
    if (!navigator.geolocation) {
        setNearbyStatus("Your browser does not support location services.", true);
        return;
    }

    setNearbyStatus("Getting your current location…");
    navigator.geolocation.getCurrentPosition(
        position => {
            const accuracy = Number(position.coords.accuracy || 0);
            nearbyUserLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy
            };
            const accuracyText = accuracy ? ` (GPS accuracy ±${Math.round(accuracy)} m)` : "";
            setNearbyStatus(`Your location: ${nearbyUserLocation.lat.toFixed(6)}, ${nearbyUserLocation.lng.toFixed(6)}${accuracyText}`);
            renderNearbyMap([]);
            searchNearbyServices();
        },
        error => {
            const messages = {
                1: "Location permission was denied. Allow location access for 127.0.0.1 in Chrome/Edge.",
                2: "Your location could not be determined. Check Windows Location Services and try again.",
                3: "Location request timed out. Please try again."
            };
            setNearbyStatus(messages[error.code] || "Unable to get your location.", true);
        },
        { enableHighAccuracy: true, timeout: 30000, maximumAge: 0 }
    );
}

function initNearbyServices() {
    const locationBtn = document.getElementById("nearbyLocationBtn");
    const radius = document.getElementById("nearbyRadius");
    const categories = document.querySelectorAll(".nearby-category");
    if (!locationBtn) return;

    locationBtn.addEventListener("click", getNearbyUserLocation);
    radius?.addEventListener("change", () => { if (nearbyUserLocation) searchNearbyServices(); });

    categories.forEach(button => {
        button.addEventListener("click", () => {
            categories.forEach(item => item.classList.remove("active"));
            button.classList.add("active");
            nearbySelectedCategory = button.dataset.category;
            if (nearbyUserLocation) searchNearbyServices();
        });
    });

    loadNearbyMapConfig();
}

window.addEventListener("resize", () => {
    if (civicAssistMap) civicAssistMap.resize();
});

initNearbyServices();
