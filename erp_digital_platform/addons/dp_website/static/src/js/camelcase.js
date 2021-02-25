// Take a single camel case string and convert it to a string of separate words (with spaces) at the camel-case boundaries.
//
// E.g.:
//    ToGetYourGEDInTimeASongAboutThe26ABCsIsOfTheEssenceButAPersonalIDCardForUser456InRoom26AContainingABC26TimesIsNotAsEasyAs123ForC3POOrR2D2Or2R2D
//                                                  --> To Get Your GED In Time A Song About The 26 ABCs Is Of The Essence But A Personal ID Card For User 456 In Room 26A Containing ABC 26 Times Is Not As Easy As 123 For C3PO Or R2D2 Or 2R2D
//    helloThere                              --> Hello There
//    HelloThere                              --> Hello There
//    ILoveTheUSA                             --> I Love The USA
//    iLoveTheUSA                             --> I Love The USA
//    DBHostCountry                           --> DB Host Country
//    SetSlot123ToInput456                    --> Set Slot 123 To Input 456
//    ILoveTheUSANetworkInTheUSA              --> I Love The USA Network In The USA
//    Limit_IOC_Duration                      --> Limit IOC Duration
//    This_is_a_Test_of_Network123_in_12_days --> This Is A Test Of Network 123 In 12 Days
//    ASongAboutTheABCsIsFunToSing                  --> A Song About The ABCs Is Fun To Sing
//    CFDs                                    --> CFDs
//    DBSettings                              --> DB Settings
//    IWouldLove1Apple                        --> 1 Would Love 1 Apple
//    Employee22IsCool                        --> Employee 22 Is Cool
//    SubIDIn                                 --> Sub ID In
//    ConfigureCFDsImmediately                --> Configure CFDs Immediately
//    UseTakerLoginForOnBehalfOfSubIDInOrders --> Use Taker Login For On Behalf Of Sub ID In Orders
//
function camelCaseToTitleCase(in_camelCaseString) {
    var split_string = in_camelCaseString.split("/");
    var split_flag = false;
    var split_space_flag = false;
    if (split_string.length > 1) {
        split_flag = true;
    }
    if (!split_flag && in_camelCaseString.includes(" ")) {
        split_string = in_camelCaseString.split(" ");
        split_space_flag = true;
    }

    for (var i=0; i<split_string.length; i++) {
        split_string[i] = split_string[i].toLowerCase();
        split_string[i] = split_string[i]                         // "ToGetYourGEDInTimeASongAboutThe26ABCsIsOfTheEssenceButAPersonalIDCardForUser456InRoom26AContainingABC26TimesIsNotAsEasyAs123ForC3POOrR2D2Or2R2D"
            .replace(/([a-z])([A-Z][a-z])/g, "$1 $2")           // "To Get YourGEDIn TimeASong About The26ABCs IsOf The Essence ButAPersonalIDCard For User456In Room26AContainingABC26Times IsNot AsEasy As123ForC3POOrR2D2Or2R2D"
            .replace(/([A-Z][a-z])([A-Z])/g, "$1 $2")           // "To Get YourGEDIn TimeASong About The26ABCs Is Of The Essence ButAPersonalIDCard For User456In Room26AContainingABC26Times Is Not As Easy As123ForC3POOr R2D2Or2R2D"
            .replace(/([a-z])([A-Z]+[a-z])/g, "$1 $2")          // "To Get Your GEDIn Time ASong About The26ABCs Is Of The Essence But APersonal IDCard For User456In Room26AContainingABC26Times Is Not As Easy As123ForC3POOr R2D2Or2R2D"
            .replace(/([A-Z]+)([A-Z][a-z][a-z])/g, "$1 $2")     // "To Get Your GEDIn Time A Song About The26ABCs Is Of The Essence But A Personal ID Card For User456In Room26A ContainingABC26Times Is Not As Easy As123ForC3POOr R2D2Or2R2D"
            .replace(/([a-z]+)([A-Z0-9]+)/g, "$1 $2")           // "To Get Your GEDIn Time A Song About The 26ABCs Is Of The Essence But A Personal ID Card For User 456In Room 26A Containing ABC26Times Is Not As Easy As 123For C3POOr R2D2Or 2R2D"

            // Note: the next regex includes a special case to exclude plurals of acronyms, e.g. "ABCs"
            .replace(/([A-Z]+)([A-Z][a-rt-z][a-z]*)/g, "$1 $2") // "To Get Your GED In Time A Song About The 26ABCs Is Of The Essence But A Personal ID Card For User 456In Room 26A Containing ABC26Times Is Not As Easy As 123For C3PO Or R2D2Or 2R2D"
            .replace(/([0-9])([A-Z][a-z]+)/g, "$1 $2")          // "To Get Your GED In Time A Song About The 26ABCs Is Of The Essence But A Personal ID Card For User 456In Room 26A Containing ABC 26Times Is Not As Easy As 123For C3PO Or R2D2Or 2R2D"

						// Note: the next two regexes use {2,} instead of + to add space on phrases like Room26A and 26ABCs but not on phrases like R2D2 and C3PO"
            .replace(/([A-Z]{2,})([0-9]{2,})/g, "$1 $2")        // "To Get Your GED In Time A Song About The 26ABCs Is Of The Essence But A Personal ID Card For User 456 In Room 26A Containing ABC 26 Times Is Not As Easy As 123 For C3PO Or R2D2 Or 2R2D"
            .replace(/([0-9]{2,})([A-Z]{2,})/g, "$1 $2")        // "To Get Your GED In Time A Song About The 26 ABCs Is Of The Essence But A Personal ID Card For User 456 In Room 26A Containing ABC 26 Times Is Not As Easy As 123 For C3PO Or R2D2 Or 2R2D"
            .trim();
        split_string[i] = split_string[i].charAt(0).toUpperCase()+ split_string[i].slice(1)
    }
    var result = [];
    if(split_flag) {
        result = split_string.join("/");
    }
    if (split_space_flag) {
        result = split_string.join(" ");
    }
    if (!split_flag && !split_space_flag && split_string.length==1) {
        result = split_string[0];
    }
  // capitalize the first letter
  return result
}

if (document.getElementById('breadcrumb_product_category')) {
    document.getElementById('breadcrumb_product_category').innerHTML = camelCaseToTitleCase(document.getElementById('breadcrumb_product_category').innerHTML)
}
if (document.getElementById('breadcrumb_product_name')) {
    document.getElementById('breadcrumb_product_name').innerHTML = camelCaseToTitleCase(document.getElementById('breadcrumb_product_name').innerHTML)
}
