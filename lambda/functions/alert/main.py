import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name="eu-west-2")
table = dynamodb.Table("OctPrices")


def lambda_handler(event, context):
    data = getData()
    alerts = []

    alerts += check_alerts(data['ERATEChange'], 25, -20, 'Electricity increase >25%',
                           'Electricity decrease >20%')
    alerts += check_alerts(data['GRATEChange'], 10, -8, 'Gas increase >10%', 'Gas decrease >8%')

    ERATE, ERATEChange, ERATEArrow, ERATEColour = format_rate_change(data['ERATE'], data['ERATEChange'])
    GRATE, GRATEChange, GRATEArrow, GRATEColour = format_rate_change(data['GRATE'], data['GRATEChange'])

    if alerts:
        res = {
            "email": EMAIL_TEMPLATE.format(ERATE=ERATE, ERATEChange=ERATEChange, ERATEColour=ERATEColour,
                                           ERATEArrow=ERATEArrow, GRATE=GRATE, GRATEChange=GRATEChange,
                                           GRATEColour=GRATEColour, GRATEArrow=GRATEArrow)
        }
    else:
        res = {}

    return res


def getData():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    rate_types = ["ERATE", "GRATE", "ESTAND", "GSTAND"]
    result = {}

    def query_rates(date, rate_type):
        response = table.query(
            KeyConditionExpression=Key('Type').eq(rate_type) & Key('Date').eq(date)
        )
        if response['Items']:
            return float(response['Items'][0].get('Value', 0))
        return None

    for rate_type in rate_types:
        tomorrow_rate = query_rates(tomorrow, rate_type)
        today_rate = query_rates(today, rate_type)

        if tomorrow_rate is None or today_rate is None:
            result[f"{rate_type}"] = ""
            result[f"{rate_type}Change"] = ""
        else:
            if today_rate != 0:
                change_percentage = ((tomorrow_rate - today_rate) / today_rate) * 100
                result[f"{rate_type}"] = f"{tomorrow_rate:.2f}"
                result[f"{rate_type}Change"] = f"{change_percentage:.2f}"
            else:
                result[f"{rate_type}"] = f"{tomorrow_rate:.2f}"
                result[f"{rate_type}Change"] = "0"

    return result


def check_alerts(rate_change, threshold_increase, threshold_decrease, message_increase, message_decrease):
    alerts = []
    rate_change_value = float(rate_change)
    if rate_change_value > threshold_increase:
        alerts.append(message_increase)
    elif rate_change_value < threshold_decrease:
        alerts.append(message_decrease)
    return alerts


def format_rate_change(rate, rate_change):
    rate_value = float(rate)
    rate_change_value = float(rate_change)
    rate_change_percentage = round(rate_change_value * 100) / 100
    if rate_change_percentage > 0:
        arrow = '&#9650;'  # Up arrow
        color = '#dc3545'  # Red
    elif rate_change_percentage < 0:
        arrow = '&#9660;'  # Down arrow
        color = '#198754'  # Green
    else:
        arrow = ''
        color = '#718096'  # Grey
    return rate_value, rate_change_percentage, arrow, color


EMAIL_TEMPLATE = """

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head>
    <!-- Compiled with Bootstrap Email version: 1.4.0 --><meta http-equiv="x-ua-compatible" content="ie=edge">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <style type="text/css">
      body,table,td{{font-family:Helvetica,Arial,sans-serif !important}}.ExternalClass{{width:100%}}.ExternalClass,.ExternalClass p,.ExternalClass span,.ExternalClass font,.ExternalClass td,.ExternalClass div{{line-height:150%}}a{{text-decoration:none}}*{{color:inherit}}a[x-apple-data-detectors],u+#body a,#MessageViewBody a{{color:inherit;text-decoration:none;font-size:inherit;font-family:inherit;font-weight:inherit;line-height:inherit}}img{{-ms-interpolation-mode:bicubic}}table:not([class^=s-]){{font-family:Helvetica,Arial,sans-serif;mso-table-lspace:0pt;mso-table-rspace:0pt;border-spacing:0px;border-collapse:collapse}}table:not([class^=s-]) td{{border-spacing:0px;border-collapse:collapse}}@media screen and (max-width: 600px){{.gap-4.row,.gap-x-4.row{{margin-right:-16px !important}}.gap-4.row>table>tbody>tr>td,.gap-x-4.row>table>tbody>tr>td{{padding-right:16px !important}}.gap-4.row,.gap-y-4.row{{margin-bottom:-16px !important}}.gap-4.row>table>tbody>tr>td,.gap-y-4.row>table>tbody>tr>td{{padding-bottom:16px !important}}.row-responsive.row{{margin-right:0 !important}}table.gap-4.stack-x>tbody>tr>td{{padding-right:16px !important}}table.gap-4.stack-y>tbody>tr>td{{padding-bottom:16px !important}}td.col-lg-6{{display:block;width:100% !important;padding-left:0 !important;padding-right:0 !important}}.w-full,.w-full>tbody>tr>td{{width:100% !important}}*[class*=s-lg-]>tbody>tr>td{{font-size:0 !important;line-height:0 !important;height:0 !important}}.s-2>tbody>tr>td{{font-size:8px !important;line-height:8px !important;height:8px !important}}.s-5>tbody>tr>td{{font-size:20px !important;line-height:20px !important;height:20px !important}}.s-10>tbody>tr>td{{font-size:40px !important;line-height:40px !important;height:40px !important}}}}
    </style>
  </head>
  <body class="bg-light" style="outline: 0; width: 100%; min-width: 100%; height: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; font-family: Helvetica, Arial, sans-serif; line-height: 24px; font-weight: normal; font-size: 16px; -moz-box-sizing: border-box; -webkit-box-sizing: border-box; box-sizing: border-box; color: #000000; margin: 0; padding: 0; border-width: 0;" bgcolor="#f7fafc">
    <table class="bg-light body" valign="top" role="presentation" border="0" cellpadding="0" cellspacing="0" style="outline: 0; width: 100%; min-width: 100%; height: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; font-family: Helvetica, Arial, sans-serif; line-height: 24px; font-weight: normal; font-size: 16px; -moz-box-sizing: border-box; -webkit-box-sizing: border-box; box-sizing: border-box; color: #000000; margin: 0; padding: 0; border-width: 0;" bgcolor="#f7fafc">
      <tbody>
        <tr>
          <td valign="top" style="line-height: 24px; font-size: 16px; margin: 0;" align="left" bgcolor="#f7fafc">
            <table class="container" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
              <tbody>
                <tr>
                  <td align="center" style="line-height: 24px; font-size: 16px; margin: 0; padding: 0 16px;">
                    <!--[if (gte mso 9)|(IE)]>
                      <table align="center" role="presentation">
                        <tbody>
                          <tr>
                            <td width="600">
                    <![endif]-->
                    <table align="center" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 600px; margin: 0 auto;">
                      <tbody>
                        <tr>
                          <td style="line-height: 24px; font-size: 16px; margin: 0;" align="left">
                            <div class="row gap-4 row-responsive" style="margin-right: -16px; margin-bottom: -16px;">
                              <table class="" role="presentation" border="0" cellpadding="0" cellspacing="0" style="table-layout: fixed; width: 100%;" width="100%">
                                <tbody>
                                  <tr>
                                    <td class="col-lg-6" style="line-height: 24px; font-size: 16px; min-height: 1px; font-weight: normal; padding-right: 16px; width: 50%; padding-bottom: 16px; margin: 0;" align="left" valign="top">
                                      <table class="s-10 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td style="line-height: 40px; font-size: 40px; width: 100%; height: 40px; margin: 0;" align="left" width="100%" height="40">
                                              &#160;
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table class="card" role="presentation" border="0" cellpadding="0" cellspacing="0" style="border-radius: 6px; border-collapse: separate !important; width: 100%; overflow: hidden; border: 1px solid #e2e8f0;" bgcolor="#ffffff">
                                        <tbody>
                                          <tr>
                                            <td style="line-height: 24px; font-size: 16px; width: 100%; margin: 0;" align="left" bgcolor="#ffffff">
                                              <table class="card-body" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
                                                <tbody>
                                                  <tr>
                                                    <td style="line-height: 24px; font-size: 16px; width: 100%; margin: 0; padding: 20px;" align="left">
                                                      <h1 class="h3  text-center" style="padding-top: 0; padding-bottom: 0; font-weight: 500; vertical-align: baseline; font-size: 28px; line-height: 33.6px; margin: 0;" align="center">Electricity Tomorrow</h1>
                                                      <table class="s-2 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 8px; font-size: 8px; width: 100%; height: 8px; margin: 0;" align="left" width="100%" height="8">
                                                              &#160;
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <table class="s-5 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 20px; font-size: 20px; width: 100%; height: 20px; margin: 0;" align="left" width="100%" height="20">
                                                              &#160;
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <table class="hr" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 24px; font-size: 16px; border-top-width: 1px; border-top-color: #e2e8f0; border-top-style: solid; height: 1px; width: 100%; margin: 0;" align="left">
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <table class="s-5 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 20px; font-size: 20px; width: 100%; height: 20px; margin: 0;" align="left" width="100%" height="20">
                                                              &#160;
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <div class="row g-0" style="margin-right: -24px;">
                                                        <table class="" role="presentation" border="0" cellpadding="0" cellspacing="0" style="table-layout: fixed; width: 100%;" width="100%">
                                                          <tbody>
                                                            <tr>
                                                              <td class="col" style="line-height: 24px; font-size: 16px; min-height: 1px; font-weight: normal; padding-right: 24px; margin: 0;" align="left" valign="top">
                                                                <span id="ERATE-Today">{ERATE} </span>p/kWh
                                                              </td>
                                                              <td class="col" style="line-height: 24px; font-size: 16px; min-height: 1px; font-weight: normal; padding-right: 24px; margin: 0;" align="left" valign="top">
                                                                <table class="badge bg-success" align="left" role="presentation" border="0" cellpadding="0" cellspacing="0" style="" bgcolor="{ERATEColour}">
                                                                  <tbody>
                                                                    <tr>
                                                                      <td style="line-height: 1; font-size: 75%; display: inline-block; font-weight: 700; white-space: nowrap; border-radius: 4px; margin: 0; padding: 4px 6.4px;" align="center" bgcolor="{ERATEColour}" valign="baseline">
                                                                        <span id="ERATE-Today-Change">{ERATEArrow} {ERATEChange}%</span>
                                                                      </td>
                                                                    </tr>
                                                                  </tbody>
                                                                </table>
                                                              </td>
                                                            </tr>
                                                          </tbody>
                                                        </table>
                                                      </div>
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table class="s-10 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td style="line-height: 40px; font-size: 40px; width: 100%; height: 40px; margin: 0;" align="left" width="100%" height="40">
                                              &#160;
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </td>
                                    <td class="col-lg-6" style="line-height: 24px; font-size: 16px; min-height: 1px; font-weight: normal; padding-right: 16px; width: 50%; padding-bottom: 16px; margin: 0;" align="left" valign="top">
                                      <table class="s-10 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td style="line-height: 40px; font-size: 40px; width: 100%; height: 40px; margin: 0;" align="left" width="100%" height="40">
                                              &#160;
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table class="card" role="presentation" border="0" cellpadding="0" cellspacing="0" style="border-radius: 6px; border-collapse: separate !important; width: 100%; overflow: hidden; border: 1px solid #e2e8f0;" bgcolor="#ffffff">
                                        <tbody>
                                          <tr>
                                            <td style="line-height: 24px; font-size: 16px; width: 100%; margin: 0;" align="left" bgcolor="#ffffff">
                                              <table class="card-body" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
                                                <tbody>
                                                  <tr>
                                                    <td style="line-height: 24px; font-size: 16px; width: 100%; margin: 0; padding: 20px;" align="left">
                                                      <h1 class="h3  text-center" style="padding-top: 0; padding-bottom: 0; font-weight: 500; vertical-align: baseline; font-size: 28px; line-height: 33.6px; margin: 0;" align="center">Gas Tomorrow</h1>
                                                      <table class="s-2 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 8px; font-size: 8px; width: 100%; height: 8px; margin: 0;" align="left" width="100%" height="8">
                                                              &#160;
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <table class="s-5 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 20px; font-size: 20px; width: 100%; height: 20px; margin: 0;" align="left" width="100%" height="20">
                                                              &#160;
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <table class="hr" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 24px; font-size: 16px; border-top-width: 1px; border-top-color: #e2e8f0; border-top-style: solid; height: 1px; width: 100%; margin: 0;" align="left">
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <table class="s-5 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                                        <tbody>
                                                          <tr>
                                                            <td style="line-height: 20px; font-size: 20px; width: 100%; height: 20px; margin: 0;" align="left" width="100%" height="20">
                                                              &#160;
                                                            </td>
                                                          </tr>
                                                        </tbody>
                                                      </table>
                                                      <div class="row g-0" style="margin-right: -24px;">
                                                        <table class="" role="presentation" border="0" cellpadding="0" cellspacing="0" style="table-layout: fixed; width: 100%;" width="100%">
                                                          <tbody>
                                                            <tr>
                                                              <td class="col" style="line-height: 24px; font-size: 16px; min-height: 1px; font-weight: normal; padding-right: 24px; margin: 0;" align="left" valign="top">
                                                                <span id="ERATE-Today">{GRATE} </span>p/kWh
                                                              </td>
                                                              <td class="col" style="line-height: 24px; font-size: 16px; min-height: 1px; font-weight: normal; padding-right: 24px; margin: 0;" align="left" valign="top">
                                                                <table class="badge bg-success" align="left" role="presentation" border="0" cellpadding="0" cellspacing="0" style="" bgcolor="{GRATEColour}">
                                                                  <tbody>
                                                                    <tr>
                                                                      <td style="line-height: 1; font-size: 75%; display: inline-block; font-weight: 700; white-space: nowrap; border-radius: 4px; margin: 0; padding: 4px 6.4px;" align="center" bgcolor="{GRATEColour}" valign="baseline">
                                                                        <span id="ERATE-Today-Change">{GRATEArrow} {GRATEChange}%</span>
                                                                      </td>
                                                                    </tr>
                                                                  </tbody>
                                                                </table>
                                                              </td>
                                                            </tr>
                                                          </tbody>
                                                        </table>
                                                      </div>
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table class="s-10 w-full" role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td style="line-height: 40px; font-size: 40px; width: 100%; height: 40px; margin: 0;" align="left" width="100%" height="40">
                                              &#160;
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </td>
                                  </tr>
                                </tbody>
                              </table>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <!--[if (gte mso 9)|(IE)]>
                    </td>
                  </tr>
                </tbody>
              </table>
                    <![endif]-->
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>


"""
