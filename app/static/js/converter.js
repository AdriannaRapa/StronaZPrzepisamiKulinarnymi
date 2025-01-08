async function convertUnits() {
    const product = document.getElementById('product').value;
    const value = parseFloat(document.querySelector('input[placeholder="ML"]').value) || parseFloat(document.querySelector('input[placeholder="GRAM"]').value);
    const inputUnit = value === parseFloat(document.querySelector('input[placeholder="ML"]').value) ? 'ml' : 'gram';
    const outputUnit = inputUnit === 'ml' ? 'gram' : 'ml';

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product, value, input_unit: inputUnit, output_unit: outputUnit })
        });

        const result = await response.json();
        if (response.ok) {
            alert(`${value} ${inputUnit} to około ${result.output_value} ${outputUnit}.`);
        } else {
            alert(result.error || 'Wystąpił błąd.');
        }
    } catch (error) {
        console.error('Błąd podczas komunikacji z backendem:', error);
        alert('Wystąpił problem z połączeniem.');
    }
}


async function convertShapes() {
    const recipeWidth = parseFloat(document.querySelector('input[placeholder="Szerokość"]:nth-of-type(1)').value);
    const recipeHeight = parseFloat(document.querySelector('input[placeholder="Wysokość"]:nth-of-type(1)').value);
    const homeWidth = parseFloat(document.querySelector('input[placeholder="Szerokość"]:nth-of-type(2)').value);
    const homeHeight = parseFloat(document.querySelector('input[placeholder="Wysokość"]:nth-of-type(2)').value);

    try {
        const response = await fetch('/api/convert_shape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ recipe_width: recipeWidth, recipe_height: recipeHeight, home_width: homeWidth, home_height: homeHeight })
        });

        const result = await response.json();
        if (response.ok) {
            alert(`Pomnóż składniki przez ${result.scaling_factor}`);
        } else {
            alert(result.error || 'Wystąpił błąd.');
        }
    } catch (error) {
        console.error('Błąd podczas komunikacji z backendem:', error);
        alert('Wystąpił problem z połączeniem.');
    }
}
