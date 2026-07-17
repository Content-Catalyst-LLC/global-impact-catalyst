<?php
/**
 * Plugin Name: Global Impact Catalyst Demo
 * Description: Browser-based Global Impact Catalyst demo for traceable impact measurement records. Shortcode: [global_impact_catalyst_demo]
 * Version: 1.0.1
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('GIC_DEMO_VERSION', '1.0.1');
define('GIC_DEMO_URL', plugin_dir_url(__FILE__));
define('GIC_DEMO_PATH', plugin_dir_path(__FILE__));

function gic_demo_register_assets() {
    wp_register_style(
        'global-impact-catalyst-demo',
        GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.css',
        array(),
        GIC_DEMO_VERSION
    );

    wp_register_script(
        'global-impact-catalyst-demo',
        GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.js',
        array(),
        GIC_DEMO_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'gic_demo_register_assets');

function gic_demo_shortcode($atts = array()) {
    static $instance = 0;
    $instance++;
    $id_prefix = 'gic-' . $instance . '-' . wp_rand(1000, 999999);

    wp_enqueue_style('global-impact-catalyst-demo');
    wp_enqueue_script('global-impact-catalyst-demo');

    ob_start();
    ?>
    <section class="gic-demo" data-gic-demo>
      <div class="gic-demo__header">
        <p class="gic-demo__eyebrow">Interactive demo</p>
        <h2>Build a Traceable Impact Record</h2>
        <p>
          Enter a goal, indicator, source, and measurement values. The demo estimates progress to target,
          flags review status, and exports a structured record for inspection.
        </p>
      </div>

      <div class="gic-demo__grid">
        <form class="gic-demo__form" data-gic-form novalidate>
          <div class="gic-demo__errors" data-gic-errors role="alert" tabindex="-1" hidden></div>
          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo esc_attr($id_prefix . '-initiative'); ?>">Initiative or program</label>
            <input id="<?php echo esc_attr($id_prefix . '-initiative'); ?>" name="initiative" type="text" required value="Community Energy Retrofit Pilot">
          </div>

          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo esc_attr($id_prefix . '-goal'); ?>">Impact goal</label>
            <textarea id="<?php echo esc_attr($id_prefix . '-goal'); ?>" name="goal" rows="3" required>Reduce household energy burden while improving residential efficiency.</textarea>
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-theme'); ?>">SDG-style theme</label>
            <select id="<?php echo esc_attr($id_prefix . '-theme'); ?>" name="sdgTheme" required>
              <option>Affordable and clean energy</option>
              <option>Climate action</option>
              <option>Sustainable cities and communities</option>
              <option>Responsible consumption and production</option>
              <option>Good health and well-being</option>
              <option>Quality education</option>
              <option>Reduced inequalities</option>
            </select>
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-indicator'); ?>">Indicator</label>
            <input id="<?php echo esc_attr($id_prefix . '-indicator'); ?>" name="indicator" type="text" required value="Average monthly bill reduction">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-unit'); ?>">Unit</label>
            <input id="<?php echo esc_attr($id_prefix . '-unit'); ?>" name="unit" type="text" required value="USD">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-direction'); ?>">Direction</label>
            <select id="<?php echo esc_attr($id_prefix . '-direction'); ?>" name="higherIsBetter" required>
              <option value="true" selected>Higher is better</option>
              <option value="false">Lower is better</option>
            </select>
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-baseline-period'); ?>">Baseline period</label>
            <input id="<?php echo esc_attr($id_prefix . '-baseline-period'); ?>" name="baselinePeriod" type="text" required value="2025 baseline">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-current-period'); ?>">Current period</label>
            <input id="<?php echo esc_attr($id_prefix . '-current-period'); ?>" name="currentPeriod" type="text" required value="2026 Q2">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-baseline'); ?>">Baseline value</label>
            <input id="<?php echo esc_attr($id_prefix . '-baseline'); ?>" name="baseline" type="number" required step="0.01" value="0">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-current'); ?>">Current value</label>
            <input id="<?php echo esc_attr($id_prefix . '-current'); ?>" name="current" type="number" required step="0.01" value="18">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-target'); ?>">Target value</label>
            <input id="<?php echo esc_attr($id_prefix . '-target'); ?>" name="target" type="number" required step="0.01" value="30">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-beneficiaries'); ?>">Beneficiaries</label>
            <input id="<?php echo esc_attr($id_prefix . '-beneficiaries'); ?>" name="beneficiaries" type="number" step="1" min="0" value="420">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-budget'); ?>">Budget USD</label>
            <input id="<?php echo esc_attr($id_prefix . '-budget'); ?>" name="budget" type="number" step="0.01" min="0" value="125000">
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-confidence'); ?>">Confidence</label>
            <select id="<?php echo esc_attr($id_prefix . '-confidence'); ?>" name="confidence">
              <option value="low">Low</option>
              <option value="medium" selected>Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div class="gic-demo__field">
            <label for="<?php echo esc_attr($id_prefix . '-review'); ?>">Review status</label>
            <select id="<?php echo esc_attr($id_prefix . '-review'); ?>" name="reviewStatus">
              <option value="draft">Draft</option>
              <option value="needs_review" selected>Needs review</option>
              <option value="reviewed">Reviewed</option>
              <option value="published">Published</option>
            </select>
          </div>

          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo esc_attr($id_prefix . '-source'); ?>">Source</label>
            <input id="<?php echo esc_attr($id_prefix . '-source'); ?>" name="source" type="text" value="Pilot utility-billing sample and participant survey summary">
          </div>

          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo esc_attr($id_prefix . '-method'); ?>">Method notes</label>
            <textarea id="<?php echo esc_attr($id_prefix . '-method'); ?>" name="method" rows="4">Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.</textarea>
          </div>

          <div class="gic-demo__actions">
            <button type="submit">Generate Record</button>
            <button type="button" data-gic-reset>Reset Example</button>
            <button type="button" data-gic-download>Download JSON</button>
          </div>
        </form>

        <aside class="gic-demo__output" aria-live="polite" aria-atomic="false">
          <div class="gic-demo__scorecard">
            <div>
              <span>Progress to target</span>
              <strong data-gic-progress role="status">—</strong>
            </div>
            <div>
              <span>Completeness / review</span>
              <strong data-gic-quality role="status">—</strong>
            </div>
            <div>
              <span>Status</span>
              <strong data-gic-status role="status">—</strong>
            </div>
          </div>

          <div class="gic-demo__bar" aria-hidden="true"><span data-gic-bar></span></div>

          <div class="gic-demo__result" data-gic-result>
            <h3>Impact Record</h3>
            <p>Generate a record to see the interpretation notes and traceability path.</p>
          </div>

          <details class="gic-demo__json">
            <summary>View JSON export</summary>
            <pre data-gic-json>{}</pre>
          </details>
        </aside>
      </div>

      <p class="gic-demo__boundary">
        Educational demo only. This is not SDG certification, ESG assurance, legal advice, or automatic truth verification.
      </p>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('global_impact_catalyst_demo', 'gic_demo_shortcode');
