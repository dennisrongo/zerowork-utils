# Canonical node type strings (API `type` values)

Extracted from the ZeroWork app bundle (`useHighlightNode-*.js` enum; also visible in
`ConnectorBuilderPage-*.js` as `nodeType:c.X` palette entries — 44 palette blocks). The REST
API accepts ANY type string with a 200 — wrong strings silently render as dead
`react-flow__node-default` husks (no card body, no config drawer, inert at run). After
`POST /node/`, verify the rendered node's class is `react-flow__node-<type>`; `node-default`
= wrong type string. Husks are undeletable via REST and clutter the canvas — get types right
the first time.

| UI block | `type` string | Official docs |
|---|---|---|
| **BROWSER** | | |
| Open Link | `open_link` | https://docs.zerowork.io/using-zerowork/using-building-blocks/open-link.md |
| Save Page URL | `save_url` | https://docs.zerowork.io/using-zerowork/using-building-blocks/save-page-url.md |
| Switch or Close Tab | `tabs` | https://docs.zerowork.io/using-zerowork/using-building-blocks/switch-or-close-tab.md |
| Go Back or Forward | `navigate` | https://docs.zerowork.io/using-zerowork/using-building-blocks/go-back-or-forward.md |
| Launch Browser | `launch_browser` | https://docs.zerowork.io/using-zerowork/using-building-blocks/launch-browser.md |
| Quit Browser | `quit_browser` | https://docs.zerowork.io/using-zerowork/using-building-blocks/quit-browser.md |
| Switch Frame | `switch_frame` | https://docs.zerowork.io/using-zerowork/using-building-blocks/switch-frame.md |
| Browser Alert | `accept_dialog` | https://docs.zerowork.io/using-zerowork/using-building-blocks/browser-alert.md |
| **WEB INTERACTION** | | |
| Click Web Element | `click` | https://docs.zerowork.io/using-zerowork/using-building-blocks/click-web-element.md |
| Check Web Element | `check` | https://docs.zerowork.io/using-zerowork/using-building-blocks/check-web-element.md |
| — Found branch | `element_present` | (branch of `check`, not a standalone page) |
| — Not Found branch | `element_absent` | (branch of `check`, not a standalone page) |
| Save Web Element | `save` | https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element.md |
| — Save Lists mode | `save` | https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element/save-lists.md |
| — Enrich Existing Data mode | `save` | https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element/enrich-existing-data.md |
| Insert Text or Data | `insert_data` | https://docs.zerowork.io/using-zerowork/using-building-blocks/insert-text-or-data.md |
| Hover Web Element | `hover` | https://docs.zerowork.io/using-zerowork/using-building-blocks/hover-web-element.md |
| Select Web Dropdown | `select` | https://docs.zerowork.io/using-zerowork/using-building-blocks/select-web-dropdown.md |
| Keyboard Action | `keyboard` | https://docs.zerowork.io/using-zerowork/using-building-blocks/keyboard-action.md |
| **LOGIC** | | |
| Start Condition | `check_dynamic_data` | https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition.md |
| Set Condition | `conditionNode` | https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition.md |
| Start Repeat | `loop` | https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat.md |
| After Repeat | `continue_after_repeat` | https://docs.zerowork.io/using-zerowork/using-building-blocks/after-repeat.md |
| Break Repeat | `loop_exit` | https://docs.zerowork.io/using-zerowork/using-building-blocks/break-repeat.md |
| Run TaskBot | `run_taskbot` | https://docs.zerowork.io/using-zerowork/using-building-blocks/run-taskbot.md |
| Start Try-Catch | `try` | https://docs.zerowork.io/using-zerowork/using-building-blocks/try-catch.md |
| After Try-Catch | `after_try` | https://docs.zerowork.io/using-zerowork/using-building-blocks/try-catch.md |
| On Catch Error | `catch` | https://docs.zerowork.io/using-zerowork/using-building-blocks/try-catch.md |
| Raise Error | `throw` | https://docs.zerowork.io/using-zerowork/using-building-blocks/raise-error.md |
| Abort Run | `abort` | https://docs.zerowork.io/using-zerowork/using-building-blocks/abort-run.md |
| **DATA** | | |
| Update Data (variable) | `update_variable` | https://docs.zerowork.io/using-zerowork/using-building-blocks/update-data.md |
| Number Operations | `math` | https://docs.zerowork.io/using-zerowork/using-building-blocks/number-operations.md |
| Format Data | `format_data` | https://docs.zerowork.io/using-zerowork/using-building-blocks/format-data.md |
| Split Text | `split_data` | https://docs.zerowork.io/using-zerowork/using-building-blocks/split-data.md |
| Apply Regex | `regex` | https://docs.zerowork.io/using-zerowork/using-building-blocks/apply-regex.md |
| Remove Duplicates | `remove_duplicate_rows` | https://docs.zerowork.io/using-zerowork/using-building-blocks/remove-duplicates.md |
| Delete Table Data | `delete_table_data` | https://docs.zerowork.io/using-zerowork/using-building-blocks/delete-data.md |
| **EXTERNAL** | | |
| Ask ChatGPT | `ask_chatgpt` | https://docs.zerowork.io/using-zerowork/using-building-blocks/ask-chatgpt.md |
| Send Notification (email) | `email` | https://docs.zerowork.io/using-zerowork/using-building-blocks/send-notification.md |
| Send HTTP Request | `update_or_configure_api` | https://docs.zerowork.io/using-zerowork/using-building-blocks/apis-send-http-request.md |
| Write JavaScript | `write_js` | https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript.md |
| **FILES** | | |
| Save File | `save_file` | https://docs.zerowork.io/using-zerowork/using-building-blocks/save-file.md |
| Upload File | `upload` | https://docs.zerowork.io/using-zerowork/using-building-blocks/upload-file.md |
| **TOOLS** | | |
| Delay | `sleep` | https://docs.zerowork.io/using-zerowork/using-building-blocks/delay.md |
| Record Date | `insert_date` | https://docs.zerowork.io/using-zerowork/using-building-blocks/record-date.md |
| Take Screenshot | `screenshot` | https://docs.zerowork.io/using-zerowork/using-building-blocks/take-screenshot.md |
| Save from Clipboard | `save_clipboard` | https://docs.zerowork.io/using-zerowork/using-building-blocks/save-from-clipboard.md |
| Log | `log` | https://docs.zerowork.io/using-zerowork/using-building-blocks/log.md |
| **Canvas-only / internal** | `sticky_note`, `fake`, `delete`, `auto-align` | https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/auto-align.md / sticky-notes.md |

## Official building-block URL set (union)

Every llms.txt page under `/using-building-blocks/` plus Launch Browser,
Quit Browser, and Run TaskBot. Each URL must be cited in a skill section
that carries Purpose / config / wiring / when-to-use / gotchas.

https://docs.zerowork.io/using-zerowork/using-building-blocks.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs/references-to-variables-and-tables.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs/code-in-inputs.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs/spintax.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/actions-and.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/actions-less-than-greater-than.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/data-found-and-data-not-found.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/contains-and-does-not-contain.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/before-date-and-after-date.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/standard-loop.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/dynamic-loop.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/continue-until-no-element-is-found.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/auto-scroll.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/auto-continue-from-last-row-or-element.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/nested-loops-handle-pagination.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/number-operations/example-standardize-different-formats.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/format-data/remove-words.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/format-data/shorten-content-length.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/imports-and-package-management.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/write-and-read-variables-and-tables.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/local-and-global-state.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/device-storage.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/utilities.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/browser-context.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/metadata.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/deactivate-building-blocks.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/shortcuts.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/sticky-notes.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/delay-times-between-the-building-blocks.md

Counterintuitive mappings that bit hard (guessed → real): `delay`→`sleep`,
`send_http`→`update_or_configure_api`, `number_operations`→`math`, `raise_error`→`throw`,
`send_notification`→`email`, `record_date`→`insert_date`, `go_back_forward`→`navigate`,
`insert_text`→`insert_data`, `break_repeat`→`loop_exit`, `start_condition`→`check_dynamic_data`,
`set_condition`→`conditionNode`, `on_catch_error`→`catch`, `after_try_catch`→`after_try`,
`try_catch`→`try`. Note `element_present`/`element_absent` are the Found/Not-Found branch
markers of `check`, not standalone configurable blocks.
