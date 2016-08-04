<html>
<head>
    <style type="text/css">
            ${css}
        </style>
    <title>OpenAcademy-Estudent.pdf</title>
    <meta charset="UTF-8">
</head>
<body>
    %for o in objects:
        <table width="100%" >
            <tr>
              <td >
                REPORTE DE COMISIONES
              </td>
              </tr>
              <tr>
              <td >
                Vendedor: ${o.user_id.name or ''}
              </td>
            </tr>
          </table>

          <table width="100%"  style="text-align: center">
            <tr>
              <td style="text-align: center">
                Factura
              </td>
              <td style="text-align: center">
                Cliente

              </td>
              <td style="text-align: center">
                Origen

              </td>
              <td style="text-align: center">
                Fecha de Factura

              </td>
              <td style="text-align: center">
                Subtotal de Factura

              </td>
              <td style="text-align: center">
                Dias de Pago

              </td>
              <td style="text-align: center">
                Comision

              </td>
            </tr>
          </table>

          %for line in o.report_lines:
          <table width="100%"  style="text-align: center">
            <tr>
              <td style="text-align: center">
                ${line.invoice_id.number or ''}
              </td>
              <td style="text-align: center">
                ${line.partner_id.name or ''}

              </td>
              <td style="text-align: center">
                ${line.origin or ''}

              </td>
              <td style="text-align: center">
                ${line.date_invoice or ''}

              </td>
              <td style="text-align: center">
                ${line.amount_payment or ''}

              </td>
              <td style="text-align: center">
                ${line.payment_days or ''}

              </td>
              <td style="text-align: center">
                ${line.comission or ''}

              </td>
            </tr>
          </table>
          %endfor

    %endfor
</body>
</html>
