# Canonical node type strings (API `type` values)

Extracted from the ZeroWork app bundle (`useHighlightNode-*.js` enum; also visible in
`ConnectorBuilderPage-*.js` as `nodeType:c.X` palette entries — 44 palette blocks). The REST
API accepts ANY type string with a 200 — wrong strings silently render as dead
`react-flow__node-default` husks (no card body, no config drawer, inert at run). After
`POST /node/`, verify the rendered node's class is `react-flow__node-<type>`; `node-default`
= wrong type string. Husks are undeletable via REST and clutter the canvas — get types right
the first time.

| UI block | `type` string |
|---|---|
| **BROWSER** | |
| Open Link | `open_link` |
| Save Page URL | `save_url` |
| Switch or Close Tab | `tabs` |
| Go Back or Forward | `navigate` |
| Launch Browser | `launch_browser` |
| Quit Browser | `quit_browser` |
| Switch Frame | `switch_frame` |
| Browser Alert | `accept_dialog` |
| **WEB INTERACTION** | |
| Click Web Element | `click` |
| Check Web Element | `check` |
| — Found branch | `element_present` |
| — Not Found branch | `element_absent` |
| Save Web Element | `save` |
| Insert Text or Data | `insert_data` |
| Hover Web Element | `hover` |
| Select Web Dropdown | `select` |
| Keyboard Action | `keyboard` |
| **LOGIC** | |
| Start Condition | `check_dynamic_data` |
| Set Condition | `conditionNode` |
| Start Repeat | `loop` |
| After Repeat | `continue_after_repeat` |
| Break Repeat | `loop_exit` |
| Run TaskBot | `run_taskbot` |
| Start Try-Catch | `try` |
| After Try-Catch | `after_try` |
| On Catch Error | `catch` |
| Raise Error | `throw` |
| Abort Run | `abort` |
| **DATA** | |
| Update Data (variable) | `update_variable` |
| Number Operations | `math` |
| Format Data | `format_data` |
| Split Text | `split_data` |
| Apply Regex | `regex` |
| Remove Duplicates | `remove_duplicate_rows` |
| Delete Table Data | `delete_table_data` |
| **EXTERNAL** | |
| Ask ChatGPT | `ask_chatgpt` |
| Send Notification (email) | `email` |
| Send HTTP Request | `update_or_configure_api` |
| Write JavaScript | `write_js` |
| **FILES** | |
| Save File | `save_file` |
| Upload File | `upload` |
| **TOOLS** | |
| Delay | `sleep` |
| Record Date | `insert_date` |
| Take Screenshot | `screenshot` |
| Save from Clipboard | `save_clipboard` |
| Log | `log` |
| **Canvas-only / internal** | `sticky_note`, `fake`, `delete`, `auto-align` |

Counterintuitive mappings that bit hard (guessed → real): `delay`→`sleep`,
`send_http`→`update_or_configure_api`, `number_operations`→`math`, `raise_error`→`throw`,
`send_notification`→`email`, `record_date`→`insert_date`, `go_back_forward`→`navigate`,
`insert_text`→`insert_data`, `break_repeat`→`loop_exit`, `start_condition`→`check_dynamic_data`,
`set_condition`→`conditionNode`, `on_catch_error`→`catch`, `after_try_catch`→`after_try`,
`try_catch`→`try`. Note `element_present`/`element_absent` are the Found/Not-Found branch
markers of `check`, not standalone configurable blocks.
