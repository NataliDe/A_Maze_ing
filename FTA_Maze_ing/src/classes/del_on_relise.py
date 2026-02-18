# def _print_menu(self, is_path_visible: bool,
#                      char_style: str,
#                      color_style: str) -> None:
#         path_action = "Hide" if is_path_visible else "Show"
#
#         print(f"{self.title}")
#         print(f"[{self.CMD_GENERATE_NEW}] Generate new maze")
#         print(f"[{self.CMD_SHOW_PATH}] {path_action} path")
#         print(f"[{self.CMD_CHAR_STYLE}] Change characters stile. Now: {char_style})")
#         print(f"[{self.CMD_CHANGE_COLORS}] Change color stile. Now: {color_style})")
#         print(f"[{self.CMD_EXIT}] Quit program")
#
#
#        iterations = self.grid.grid_height * self.grid.grid_width * 10
#         if first_generation:
#             self.builder.init_vectors()
#             for i in range(iterations):
#                 self.builder.step()
#                 self.renderer.draw_cell()
#         else:
