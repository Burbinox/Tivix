async function login(){
    let username = document.getElementById("log_username").value;
    let password = document.getElementById("log_password").value;
    const response = await fetch(`http://127.0.0.1:8000/login?username=${username}&password=${password}`, {method: 'POST'})
    let data = await response.json()
    let message = document.getElementById('message');
    message.innerText = data;
    if (response.status === 202){
        let get_budgets = document.createElement("BUTTON")
        let button_text = document.createTextNode("Get Your Budgets")
        get_budgets.appendChild(button_text)
        get_budgets.setAttribute("type", "button")
        get_budgets.setAttribute("onclick", "get_budgets()")
        get_budgets.setAttribute("id", "budget_button")
        let elem = document.getElementById("get_budgets")
        elem.appendChild(get_budgets)
    }

}

async function register(){
    let username = document.getElementById("reg_username").value;
    let password = document.getElementById("reg_password").value;
    fetch(`http://127.0.0.1:8000/register?username=${username}&password=${password}`, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data)
            let message = document.getElementById('message');
            message.innerText = data
        })
}


async function get_budgets(){
    const response = await fetch("http://127.0.0.1:8000/budget")
    let data = await response.json()
    console.log(data[0])
    if (response.status === 200){
        let budgets = document.createElement("p")
        let budget_text = document.createTextNode(data[0])
        budgets.appendChild(budget_text)
        let elem = document.getElementById("budgets")
        elem.appendChild(budgets)
    }
}