export default function ResultTable({

    headers = [],

    rows = []
}) {

    return (

        <table className="result-table">

            <thead>

                <tr>

                    {
                        headers.map((header, index) => (

                            <th key={index}>

                                {header}

                            </th>
                        ))
                    }

                </tr>

            </thead>

            <tbody>

                {
                    rows.map((row, rowIndex) => (

                        <tr key={rowIndex}>

                            {
                                row.map((cell, cellIndex) => (

                                    <td key={cellIndex}>

                                        {cell}

                                    </td>
                                ))
                            }

                        </tr>
                    ))
                }

            </tbody>

        </table>
    );
}