export function upload(selector) {
    const input = document.querySelector(selector)

    const open = document.createElement('button')
    open.classList.add('btn')
    open.textContent = 'Open'

    input.inserAdjacentElement('afterend', open)

    const triggerInput = () => input.click()

    const changeHandler = event => {
        console.log(event)
    }

    open.addEventListener('click', triggerInput)
    input.addEventListener('change', changeHandler)
}