const API_URL = "http://localhost:5003";

document.getElementById("feedbackForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    const complaintId = document.getElementById("complaintId").value;
    const actuallySolved = document.getElementById("actuallySolved").value;
    const rating = document.getElementById("rating").value;
    const comments = document.getElementById("comments").value;

    const response = await fetch(API_URL + "/feedback/" + complaintId, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        actually_solved: actuallySolved,
        satisfaction_rating: parseInt(rating),
        comments: comments
      })
    });
    const data = await response.json();
    const resultDiv = document.getElementById("feedbackResult");

    if (!response.ok) {
      resultDiv.className = "";
      resultDiv.innerHTML = `<b>Error:</b> ${data.error}`;
      return;
    }

    if (data.actually_solved === "No") {
      resultDiv.className = "priority-alert";
      resultDiv.innerHTML =
        `<h3>Marked as Priority</h3>
         This complaint was reported as NOT solved.
         We are making this a top priority for review.<br><br>
         Complaint Status (system): ${data.complaint_status}<br>
         Rating: ${data.satisfaction_rating}/5`;
    } else {
      resultDiv.className = "";
      resultDiv.innerHTML =
        `<h3>Feedback Submitted</h3>
         Complaint Status: ${data.complaint_status}<br>
         Actually Solved: ${data.actually_solved}<br>
         Rating: ${data.satisfaction_rating}/5`;
    }
  });

document.getElementById("schemeForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    const citizenId = document.getElementById("citizenId").value;
    const units = document.getElementById("units").value;
    const isWoman = document.getElementById("isWoman").checked;

    const response = await fetch(API_URL + "/scheme/" + citizenId, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        units_consumed: parseInt(units),
        is_woman: isWoman
      })
    });
    const data = await response.json();
    const resultDiv = document.getElementById("schemeResult");

    if (!response.ok) {
      resultDiv.innerHTML = `<b>Error:</b> ${data.error}`;
      return;
    }

    resultDiv.innerHTML =
      `<h3>Bill for ${data.citizen_name}</h3>
       Units Consumed: ${data.units_consumed} (First ${data.free_units} free - Gruha Jyothi)<br>
       Electricity Charge: Rs. ${data.electricity_charge_before_lakshmi}<br>
       ${data.is_woman ? `Gruha Lakshmi Discount: Rs. ${data.gruha_lakshmi_amount}<br>` : ""}
       <span class="bill-amount">Final Amount Payable: Rs. ${data.final_amount}</span>`;
  });